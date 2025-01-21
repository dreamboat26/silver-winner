from llama_index.core.llms.llm import LLM
from llama_index.core.prompts.base import PromptTemplate


from models import Slide, SlideInfo

COMPOSE_SLIDE_PROMPT = """
The key to creating a perfect slide for a presentation is following:
Be concise: Avoid overloading slides with text or data. Stick to one atomic core idea per slide.
Incorporate emotion: Make your audience feel something—excitement, curiosity, or inspiration through the narration
Use data wisely: Visualize key stats (charts, infographics) but don’t overwhelm with too much detail.
The content of each slide can be narrated under 20 seconds.

Your responsibility is to create one slide and the narration for that slide. The slide is part of a presentation on the topis: "{topic}".
The title of this slide is: "{title}".
The core idea to discuss in this slide is: "{core_idea}".
{prev_next_info}You must make sure the content of this slide never overlaps with other slides. the content in this slide must be ONLY about "{core_idea}". always remember for crafting the perfect slide, LESS IS MORE, keep the texts and diagram minimal, and do the explanation during narration.
now write the contents of that slide in markdown, the format must be valid markdown, you can write code snippets, tables or even latex for math and equation if you want. If you need to draw a diagram, you can use mermaid to draw various types of diagrams. Just put the mermaid definition in a code block with the language set to "mermaid". For example:
```mermaid
<mermaid definition code here>
```
Make sure the mermaid code is valid and error-free. Use simple diagram for ensure error-free.
LESS IS MORE, keep the texts and diagram minimal so that they fit in one slide and don't look cluttered. You MUST ENSURE that one line does not have more than 7-8 words, this is very important for readability. Each line must be independent and COMPLETE. NEVER break in the middle of a line. Never add more than 2-3 lines(excluding diagram) per slide. Instead of too much text, prioritize using a nice minimal diagram. Do most of the explanation during narration. Try not to break the flow from previous slide or to the next slide during narration. The narration must explain the contents in the slide, but concise enough so that the audience is not bored. the narration must be under 20 seconds. Don't start the narration with "In this slide" or anything similar, just start with the content directly.
"""


async def compose_slide(
    topic: str, slide_info: SlideInfo, prev_next_info: str, llm: LLM
) -> Slide:
    title = slide_info.title
    core_idea = slide_info.atomic_core_idea
    prompt = PromptTemplate(COMPOSE_SLIDE_PROMPT)
    return await llm.astructured_predict(
        Slide,
        prompt=prompt,
        topic=topic,
        title=title,
        core_idea=core_idea,
        prev_next_info=prev_next_info,
    )
