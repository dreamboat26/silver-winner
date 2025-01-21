from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.llms.llm import LLM

ITINERARY_WRITE_PROMPT = """
You're a seasoned travel planner with a knack for finding the best deals and exploring new destinations. You're known for your attention to detail
and your ability to make travel planning easy for customers.

Based on the user's request, flight, hotel and sights information given below, write an itinerary for a customer who is planning a trip to {destination}.
---
{flights_info}
---
{hotels_info}
---
{sights_info}
---
User's request: {query}
---
Compile the whole travel plan into a summary for the customer in a nice format that is easy to follow by everyone. The travel plan must follow any instruction from the user's request. Nicely structure the itinerary with different sections for flights, accomodation, day-by-day plan etc. The itenerary must be in markdown format.

The full itinerary in markdown following the user's request: """


async def write_itinerary(
    query: str,
    destination: str,
    flights_info: str,
    hotels_info: str,
    sights_info: str,
    llm: LLM,
) -> str:
    print("\n> Writing itinerary. This may take a minute...\n")
    prompt = PromptTemplate(ITINERARY_WRITE_PROMPT)
    response = await llm.apredict(
        prompt,
        destination=destination,
        flights_info=flights_info,
        hotels_info=hotels_info,
        sights_info=sights_info,
        query=query,
    )

    return response
