import os
import subprocess
import pickle
from typing import Any, List

from llama_index.core.llms.llm import LLM
from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
)
from llama_index.core.workflow.retry_policy import ConstantDelayRetryPolicy

from models import PresentationStructure, StructureFeedback, Slide, SlideInfo
from agents.structure_creater import create_presentation_structure
from agents.structure_validator import validate_presentation_structure
from agents.structure_updater import update_presentation_structure
from agents.slide_maker import compose_slide
from utils import get_presentation_config, get_safe_foldername, sanitize_markdown


class StructureRequestReceived(Event):
    topic: str


class ValidateStructureRequestReceived(Event):
    structure: PresentationStructure


class UpdateStructureRequestReceived(Event):
    structure: PresentationStructure
    feedback: StructureFeedback


class StructureFinalized(Event):
    structure: PresentationStructure


class ComposeSlideRequestReceived(Event):
    slide_index: int
    slide_info: SlideInfo


class SlideCreated(Event):
    slide_index: int
    content: str
    narration: str


class PresenterWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.llm = llm

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> StructureRequestReceived:
        topic = ev.query
        await ctx.set("topic", topic)
        presentation_folder = os.path.join("presentations", get_safe_foldername(topic))
        await ctx.set("presentation_folder", presentation_folder)
        if not os.path.exists(presentation_folder):
            os.makedirs(presentation_folder)
        structure_file = os.path.join(presentation_folder, "structure.pkl")
        if os.path.exists(structure_file):
            print(
                f"\n> Presentation structure already exists for topic: {topic}."
                " Skipping structure creation and using the existing structure.\n"
            )
            with open(structure_file, "rb") as f:
                structure = pickle.load(f)
            return StructureFinalized(structure=structure)
        return StructureRequestReceived(topic=topic)

    @step
    async def create_presentation_structure(
        self, ctx: Context, ev: StructureRequestReceived
    ) -> ValidateStructureRequestReceived:
        topic = ev.topic
        initial_structure = create_presentation_structure(topic, self.llm)
        return ValidateStructureRequestReceived(structure=initial_structure)

    @step
    async def validate_presentation_structure(
        self, ctx: Context, ev: ValidateStructureRequestReceived
    ) -> UpdateStructureRequestReceived | StructureFinalized:
        structure = ev.structure
        topic = await ctx.get("topic")
        feedback = validate_presentation_structure(topic, structure, self.llm)
        if feedback.is_perfect:
            return StructureFinalized(structure=structure)
        return UpdateStructureRequestReceived(structure=structure, feedback=feedback)

    @step
    async def update_presentation_structure(
        self, ctx: Context, ev: UpdateStructureRequestReceived
    ) -> StructureFinalized:
        structure = ev.structure
        feedback = ev.feedback
        topic = await ctx.get("topic")
        updated_structure = update_presentation_structure(
            topic, structure, feedback, self.llm
        )
        # pickle the structure in the presentation folder
        structure_file = os.path.join(
            await ctx.get("presentation_folder"), "structure.pkl"
        )
        with open(structure_file, "wb") as f:
            pickle.dump(updated_structure, f)
        return StructureFinalized(structure=updated_structure)

    @step
    async def create_slides(
        self, ctx: Context, ev: StructureFinalized
    ) -> ComposeSlideRequestReceived:
        structure = ev.structure
        await ctx.set("structure", structure)
        await ctx.set("num_slides", len(structure.slides))
        for slide_index, slide in enumerate(structure.slides):
            ctx.send_event(
                ComposeSlideRequestReceived(slide_index=slide_index, slide_info=slide)
            )

    @step(num_workers=6, retry_policy=ConstantDelayRetryPolicy())
    async def compose_one_slide(
        self, ctx: Context, ev: ComposeSlideRequestReceived
    ) -> SlideCreated:
        slide_index = ev.slide_index
        slide_info = ev.slide_info
        print(f"\n> Creating slide: {slide_info.title}...\n")
        presentation_folder = await ctx.get("presentation_folder")
        slide_folder = os.path.join(presentation_folder, f"slide_{slide_index}")
        if not os.path.exists(slide_folder):
            os.makedirs(slide_folder)
        content_file = os.path.join(slide_folder, "content.md")
        narration_file = os.path.join(slide_folder, "narration.txt")
        if os.path.exists(content_file) and os.path.exists(narration_file):
            with open(content_file, "r") as f:
                content = f.read()
            with open(narration_file, "r") as f:
                narration = f.read()
            return SlideCreated(
                slide_index=slide_index, content=content, narration=narration
            )
        topic = await ctx.get("topic")
        structure = await ctx.get("structure")
        slides_info: List[SlideInfo] = structure.slides
        num_slides = await ctx.get("num_slides")
        prev_next_info = ""
        if slide_index > 0:
            prev_next_info += f'The previous slide is "{slides_info[slide_index-1].title}"({slides_info[slide_index-1].atomic_core_idea}). '
        if slide_index < num_slides - 1:
            prev_next_info += f'The next slide is "{slides_info[slide_index+1].title}"({slides_info[slide_index+1].atomic_core_idea}). '
        slide = await compose_slide(topic, slide_info, prev_next_info, self.llm)
        content = slide.content
        narration = slide.narration
        with open(content_file, "w") as f:
            f.write(content)
        with open(narration_file, "w") as f:
            f.write(narration)
        return SlideCreated(
            slide_index=slide_index, content=content, narration=narration
        )

    @step
    async def combine_slides(self, ctx: Context, ev: SlideCreated) -> StopEvent:
        num_slides = await ctx.get("num_slides")
        presentation_folder = await ctx.get("presentation_folder")
        events = ctx.collect_events(ev, [SlideCreated] * num_slides)
        if events is None:
            return None

        slide_created_events: List[SlideCreated] = events
        slides_dict = {
            ev.slide_index: f"{ev.content}\n\nNote:\n{ev.narration}\n"
            for ev in slide_created_events
        }
        slides_list = [slides_dict[i] for i in range(num_slides)]
        slides_separator = "\n\n[comment]: # (!!!)\n\n"
        full_presentation_template = sanitize_markdown(
            slides_separator.join(slides_list)
        )
        full_presentation_template = (
            get_presentation_config() + full_presentation_template
        )
        template_file = os.path.join(presentation_folder, "presentation_template.md")
        with open(template_file, "w") as f:
            f.write(full_presentation_template)

        # using mermaid-cli to render mermaid diagrams
        print("\n> Rendering diagrams...\n")
        presentation_file = os.path.join(presentation_folder, "presentation.md")
        subprocess.run(
            ["mmdc", "-i", template_file, "-o", presentation_file, "-e", "png"]
        )

        with open(presentation_file, "r") as f:
            presentation_content = f.read()
        with open(presentation_file, "w") as f:
            f.write(sanitize_markdown(presentation_content))

        media_dir = os.path.join(presentation_folder, "media")
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
        # copy all png files from presentation folder to media folder
        for filename in os.listdir(presentation_folder):
            if filename.endswith(".png"):
                os.rename(
                    os.path.join(presentation_folder, filename),
                    os.path.join(media_dir, filename),
                )

        # using mdslides to render presentation
        print("\n> Rendering presentation...\n")
        output_dir = os.path.join(presentation_folder, "output")
        html_file = os.path.join(output_dir, "index.html")
        pdf_file = os.path.join(presentation_folder, "presentation.pdf")
        subprocess.run(
            [
                "mdslides",
                presentation_file,
                "--include",
                media_dir,
                "--output_dir",
                output_dir,
            ]
        )
        print(
            f'\n> Presentation rendered. Run "open {html_file}" to view the presentation.\n'
        )

        print("\n> Exporting presentation to PDF...\n")
        subprocess.run(
            [
                "decktape",
                "--headless=true",
                "--screenshots",
                "--screenshots-directory=.",
                "reveal",
                html_file,
                pdf_file,
            ]
        )
        print(f'\n> Exported presentation to PDF. Open it using "open {pdf_file}"\n')

        return StopEvent(result=presentation_folder)
