from llama_index.core.llms.llm import LLM
from llama_index.core.prompts.base import PromptTemplate


from models import PresentationStructure, StructureFeedback

PRESENTATION_STRUCTURE_VALIDATOR_PROMPT = """
you are world's best presentation creator with 10 years of experience, you've created hundreds of perfect presentations and every single one of them kept the audience captive for the whole time. your apprentice prepared a presentation structure, and you need to make sure all the slides contain just one atomic core idea and their content can be narrated under 40-50 seconds. If you think some slides are too broad, you must ask the apprentice to break them down into separate multiple smaller atomic slides without breaking the flow and you must tell them what those updated atomic slides should contain.
The presentation on the topic: "{topic}"
Here is the initial structure the apprentice created:
---
{structure}
---
Now think very closely about all the slides above, and tell me if some of those slides are broad and need to be broken down into multiple separate slides or not. if not and if all of them are perfectly atomic, that's good otherwise just tell the which slides needs to broken down and how without breaking the flow.
"""


def validate_presentation_structure(
    topic: str, structure: PresentationStructure, llm: LLM
) -> StructureFeedback:
    print("\n> Getting expert feedback about the presentation structure...\n")
    structure_strs = []
    for i, slide in enumerate(structure.slides):
        structure_strs.append(
            f"Slide {i+1}"
            f"\nTitle: {slide.title}"
            f"\nCore Idea for this slide: {slide.atomic_core_idea}"
        )
    prompt = PromptTemplate(PRESENTATION_STRUCTURE_VALIDATOR_PROMPT)
    structure_str = "\n\n".join(structure_strs)
    # print(structure_str)
    return llm.structured_predict(
        StructureFeedback,
        prompt=prompt,
        topic=topic,
        structure=structure_str,
    )
