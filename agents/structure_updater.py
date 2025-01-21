from llama_index.core.llms.llm import LLM
from llama_index.core.prompts.base import PromptTemplate


from models import PresentationStructure, StructureFeedback

PRESENTATION_STRUCTURE_UPDATE_PROMPT = """
You are trying to come up with the best structure for a presentation on the topic: "{topic}".
Here is the current structure:
---
{structure}
---
But you have made some mistakes, some slides are too broad and does not represent an atomic core idea. The best presentation creator in the world has reviewed your structure and has given you feedback on how to improve it. Here is the feedback:
---
{feedback}
---
Now read the feedback carefully and resolve every single issue mentioned in the feedback without breaking the flow. Make sure all the issues are addressed and the structure is perfect. Each slide must contain one atomic core idea and can be narrated in 40-50 seconds. Now give me the updated structure for the presentation without breaking the flow of the slides.
"""


def update_presentation_structure(
    topic: str, structure: PresentationStructure, feedback: StructureFeedback, llm: LLM
) -> PresentationStructure:
    print("\n> Updating presentation structure...\n")
    structure_strs = []
    for i, slide in enumerate(structure.slides):
        structure_strs.append(
            f"Slide {i+1}"
            f"\nTitle: {slide.title}"
            f"\nCore Idea for this slide: {slide.atomic_core_idea}"
        )
    structure_str = "\n\n".join(structure_strs)
    # print(f"Current structure:\n{structure_str}")
    # print(f"Feedback:\n{feedback.is_perfect}")
    # print(f"Feedback:\n{feedback.feedback}")
    prompt = PromptTemplate(PRESENTATION_STRUCTURE_UPDATE_PROMPT)
    return llm.structured_predict(
        PresentationStructure,
        prompt=prompt,
        topic=topic,
        structure=structure_str,
        feedback=feedback.feedback,
    )
