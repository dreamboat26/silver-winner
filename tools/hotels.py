import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch


load_dotenv()


def get_formatted_hotels_info(hotels: list) -> str:
    formatted_hotels = []
    for hotel in hotels:
        formatted_hotels.append(hotel["name"])
        formatted_hotels.append(f"Rate per night: {hotel['rate_per_night']['lowest']}")
        if "overall_rating" in hotel:
            formatted_hotels.append(
                f"Rating: {hotel['overall_rating']} ({hotel['reviews']})"
            )
        if "location_rating" in hotel:
            formatted_hotels.append(f"Location Rating: {hotel['location_rating']}")
        formatted_hotels.append(f"Amenities: {', '.join(hotel['amenities'][:7])}")
        if "images" in hotel and len(hotel["images"]) > 0:
            formatted_hotels.append(f"Image: {hotel['images'][0]['thumbnail']}")
        formatted_hotels.append("")
    return "\n".join(formatted_hotels)


def find_hotels(
    city: str = Field(..., description="The city where the hotels are located"),
    check_in_date: str = Field(
        ..., description="The check-in date in the format YYYY-MM-DD"
    ),
    check_out_date: str = Field(
        None, description="The check-out date in the format YYYY-MM-DD"
    ),
) -> str:
    """
    Find hotels in a specific city.
    """

    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    params = {
        "engine": "google_hotels",
        "q": city,
        "hl": "en",
        "gl": "us",
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "currency": "USD",
        "api_key": SERPAPI_KEY,
    }

    try:
        print(f"\n> Finding hotels in {city}\n")
        search = GoogleSearch(params)
        results = search.get_dict()
        if "error" in results:
            raise ValueError(f"SerpAPI error: {results['error']}")
        hotels_data = results.get("properties", [])
        first_line = f"Accommodations in {city}:"
        return first_line + "\n\n" + get_formatted_hotels_info(hotels_data[:5])
    except Exception as e:
        raise Exception(f"Failed to find hotels: {str(e)}")
