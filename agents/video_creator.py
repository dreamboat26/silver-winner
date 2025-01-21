from typing import Any
import subprocess
import shlex
import os
import json
import pickle

from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
)
from llama_index.core.workflow.retry_policy import ConstantDelayRetryPolicy

from models import PresentationStructure
from agents.narrator import narrate


class NarrationRequestReceived(Event):
    slide_index: int


class SlideNarrated(Event):
    slide_index: int


class SlideClipCreated(Event):
    slide_index: int
    clip_file: str


class PresenterVideoCreaterWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        model: str,
        voice: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.model = model
        self.voice = voice

    @step
    async def start(
        self, ctx: Context, ev: StartEvent
    ) -> NarrationRequestReceived | StopEvent:
        presentation_dir = ev.presentation_dir
        await ctx.set("presentation_dir", presentation_dir)
        structure_file = os.path.join(presentation_dir, "structure.pkl")
        if not os.path.exists(structure_file):
            return StopEvent(result="No structure found")
        with open(structure_file, "rb") as f:
            structure: PresentationStructure = pickle.load(f)
        await ctx.set("structure", structure)
        slides = structure.slides
        await ctx.set("num_slides", len(slides))
        for i in range(len(slides)):
            ctx.send_event(NarrationRequestReceived(slide_index=i))

    @step(num_workers=5, retry_policy=ConstantDelayRetryPolicy())
    async def narrate_slide(
        self, ctx: Context, ev: NarrationRequestReceived
    ) -> SlideNarrated:
        slide_index = ev.slide_index
        presentation_dir = await ctx.get("presentation_dir")
        slide_dir = os.path.join(presentation_dir, f"slide_{slide_index}")
        narration_file = os.path.join(slide_dir, "narration.txt")
        narration_audio_file = os.path.join(slide_dir, "narration.mp3")
        print(f"\n> Narrating slide_{slide_index}\n")
        if os.path.exists(narration_audio_file):
            return SlideNarrated(slide_index=slide_index)
        with open(narration_file, "r") as f:
            narration = f.read()
        await narrate(narration, self.voice, self.model, narration_audio_file)
        return SlideNarrated(slide_index=slide_index)

    @step(num_workers=5, retry_policy=ConstantDelayRetryPolicy())
    async def create_slide_clip(
        self, ctx: Context, ev: SlideNarrated
    ) -> SlideClipCreated:
        slide_index = ev.slide_index
        presentation_dir = await ctx.get("presentation_dir")
        slide_dir = os.path.join(presentation_dir, f"slide_{slide_index}")
        slide_clip_file = os.path.join(slide_dir, "clip.mp4")
        print(f"\n> Creating clip for slide_{slide_index}\n")
        if os.path.exists(slide_clip_file):
            return SlideClipCreated(slide_index=slide_index, clip_file=slide_clip_file)
        slide_ss_file = os.path.join(
            presentation_dir, f"presentation_{slide_index+1}_1280x720.png"
        )
        slide_audio_file = os.path.join(slide_dir, "narration.mp3")
        file_duration_command = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            slide_audio_file,
        ]
        result = subprocess.run(
            file_duration_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = json.loads(result.stdout)
        duration = float(output["format"]["duration"]) / 1.4 + 0.5
        subprocess.run(
            shlex.split(
                f"""ffmpeg -loop 1 -i {slide_ss_file} -i {slide_audio_file} -c:v libx264 -c:a aac -b:a 192k -shortest -t {duration} -vf "format=yuv420p" -filter:a "atempo=1.4" {slide_clip_file}"""
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f"\n> Created clip for slide_{slide_index}\n")
        return SlideClipCreated(slide_index=slide_index, clip_file=slide_clip_file)

    @step
    async def combine_clips(self, ctx: Context, ev: SlideClipCreated) -> StopEvent:
        num_slides = await ctx.get("num_slides")
        presentation_dir = await ctx.get("presentation_dir")
        events = ctx.collect_events(ev, [SlideClipCreated] * num_slides)
        if not events:
            return None
        all_clips_file = os.path.join(presentation_dir, "clips.txt")
        clips = []
        for i in range(num_slides):
            clip_file = os.path.join(f"slide_{i}", "clip.mp4")
            clips.append(f"file '{clip_file}'")
        with open(all_clips_file, "w") as f:
            f.write("\n".join(clips))
        presentation_video_file = os.path.join(presentation_dir, "presentation.mp4")
        print("\n> Rendering full presentation video...\n")
        subprocess.run(
            shlex.split(
                f"""ffmpeg -y -f concat -safe 0 -i {all_clips_file} -c copy {presentation_video_file}"""
            ),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        print(f'\n> Presentation video created: "open {presentation_video_file}"\n')
        return StopEvent(result="Presentation video created")
