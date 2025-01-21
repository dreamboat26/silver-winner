from llama_index.core.llms.llm import LLM
from llama_index.core.prompts.base import PromptTemplate


from models import PresentationStructure

PRESENTATION_STRUCTURE_PROMPT = """
The key to creating a perfect presentation is following:
1. Understand Your Purpose and Audience
Define your goal: Why are you presenting? To inform, persuade, entertain, or inspire?
Key takeaway: Identify the one thing you want your audience to remember.
2. Develop a Clear Structure
Organize your content into a logical flow:
Introduction: Grab attention, introduce yourself, state your topic, and outline what the audience will gain.
Example: Start with a shocking fact, a question, or a story.
Main Content: Break your message into some main points to keep it digestible.
Use evidence, examples, and visuals to support each point.
Conclusion: Summarize key points and end with a powerful call-to-action or closing statement.
3. Craft Powerful Content
Use storytelling: People connect with narratives. Frame your points as stories, with a beginning, middle, and end.
Be concise: Avoid overloading slides with text or data. Stick to one atomic core idea per slide.
Incorporate emotion: Make your audience feel something—excitement, curiosity, or inspiration.
Use data wisely: Visualize key stats (charts, infographics) but don’t overwhelm with too much detail.
Minimal Text: Use bullet points sparingly (6x6 rule: no more than 6 words per line and 6 lines per slide).
The first slide should only contain the title and optionally a diagram, nothing else.
EACH SLIDE MUST CONTAIN ONE ATOMIC CORE IDEA, and the content of each slide can be narrated in 40-50 seconds.

Now read these guidlines thoroughly and you will create the best presentation structure on the topic: "{topic}"
Figure out how many slides there should be and what should be on each slide. EACH SLIDE MUST CONTAIN ONE ATOMIC CORE IDEA. You MUST NOT make the contents of the slides too broad or too detailed. Break down broad topics into smaller atomic slides. More slides are better than few broad slides. Make sure the content of each slide can be narrated in 40-50 seconds. Now give me the title and core atomic idea for all the slides in the presentation in order. Your structure will be critiqued by the best presentation experts in the world. So make sure you follow the guidelines and make the structure perfect. The most important thing is to make sure that the content of each slide are atomic and can be narrated in 40-50 seconds.
"""


def create_presentation_structure(topic: str, llm: LLM) -> PresentationStructure:
    print("\n> Creating presentation structure...\n")
    prompt = PromptTemplate(PRESENTATION_STRUCTURE_PROMPT)
    return llm.structured_predict(PresentationStructure, prompt=prompt, topic=topic)
