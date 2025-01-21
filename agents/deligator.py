from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.llms.llm import LLM


class TourInfo(BaseModel):
    airport_from: str = Field(
        ...,
        description="The valid 3-letter IATA airport code for the departure airport e.g. LHR, LAX etc.",
    )
    airport_to: str = Field(
        ...,
        description="The valid 3-letter IATA airport code for the destination airport e.g. LHR, LAX etc.",
    )
    departure_date: str = Field(
        ..., description="The departure date in the format YYYY-MM-DD"
    )
    return_date: str = Field(
        ..., description="The return date in the format YYYY-MM-DD"
    )
    destination: str = Field(
        ...,
        description="The destination where the user wants to visit.",
    )


class ExtractedInfo(BaseModel):
    reasoning: str = Field(
        ...,
        description="Your reasoning under 10 words behind the extracted information.",
    )
    tour_info: Optional[TourInfo] = Field(
        None, description="The extracted tour information."
    )


TOUR_PLANNER_PROMPT = """
You're a seasoned travel planner with a knack for finding the best deals and exploring new destinations. You're known for your attention to detail
and your ability to make travel planning easy for customers.

From the user's request, you have to find the following information: the IATA code of the departure airport, the IATA code of the arrival airport, the departure date, the return date and the destination. If the user has not provided the return date, you should assume that the user is planning a one-week trip. Today's date is {date_today}.

User's request: {query}
Now extract the necessary information from the user's request."""


async def extract_tour_information(query: str, llm: LLM) -> ExtractedInfo:

    prompt = PromptTemplate(TOUR_PLANNER_PROMPT)
    response = llm.structured_predict(
        ExtractedInfo,
        prompt,
        query=query,
        date_today=datetime.now().strftime("%B %d, %Y"),
    )

    # print(f"\n> Done extracting user's request: {response}\n")
    print(f"\n> Done extracting user's request\n")

    return response
