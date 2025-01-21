from typing import List, Optional
from pydantic import BaseModel, Field


class SlideInfo(BaseModel):
    title: str = Field(..., description="Title of the slide")
    atomic_core_idea: str = Field(
        ..., description="Atomic core idea for the content of this particular slide"
    )


class PresentationStructure(BaseModel):
    slides: List[SlideInfo] = Field(
        ..., description="List of slides information in the presentation"
    )


class StructureFeedback(BaseModel):
    is_perfect: bool = Field(
        ...,
        description="Whether all the slides represent atomic core ideas and can be narrated in 40-50 seconds",
    )
    feedback: Optional[str] = Field(
        None,
        description="If all the slides are not perfect then feedback on which slides need to be broken down and how",
    )


class Slide(BaseModel):
    content: str = Field(
        ...,
        description="The content of the slide in valid markdown, with no more than 6 words per line",
    )
    narration: str = Field(
        ...,
        description="Narration for the slide. The content should be narrated in 40-60 seconds",
    )
