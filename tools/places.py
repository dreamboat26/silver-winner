import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()


def get_formatted_places_info(sights: list) -> str:
    formatted_places = []
    for sight in sights:
        formatted_places.append(sight["title"])
        formatted_places.append(f"Description: {sight.get('description', 'N/A')}")
        if "rating" in sight:
            formatted_places.append(f"Rating: {sight['rating']} ({sight['reviews']})")
        formatted_places.append(f"Price: {sight.get('price', 'N/A')}")
        formatted_places.append(f"Image: {sight.get('thumbnail', 'N/A')}")
        formatted_places.append("")
    return "\n".join(formatted_places)


def find_places_to_visit(
    location: str = Field(..., description="The location to find places to visit."),
) -> str:
    """
    Find places to visit in a specific city.
    """

    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    params = {
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "q": f"top sights in {location}",
        "location": "Austin, Texas, United States",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
    }

    try:
        print(f"\n> Finding places to visit in {location}\n")
        search = GoogleSearch(params)
        results = search.get_dict()
        if "error" in results:
            raise ValueError(f"SerpAPI error: {results['error']}")
        places_data = results.get("top_sights", {"sights": []})["sights"]
        first_line = f"Here are the top places to visit in {location}:"
        return first_line + "\n\n" + get_formatted_places_info(places_data)
    except Exception as e:
        raise Exception(f"Failed to find places: {str(e)}")
