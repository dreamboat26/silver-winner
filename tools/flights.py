from typing import Optional
import os

from pydantic import Field
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()


def format_minutes(total_minutes):
    try:
        # Ensure the input is a non-negative integer
        if not isinstance(total_minutes, int) or total_minutes < 0:
            raise ValueError("Total minutes must be a non-negative integer.")
        hours = total_minutes // 60  # Calculate hours
        minutes = total_minutes % 60  # Calculate remaining minutes
        # Format the output based on hours and minutes
        if hours > 0 and minutes > 0:
            return f"{hours} hr {minutes} min"
        elif hours > 0:
            return f"{hours} hr"
        else:
            return f"{minutes} min"
    except Exception as e:
        raise ValueError(f"Failed to format minutes: {str(e)}")


def format_one_flight(
    flight_no: str,
    dep_port: str,
    arr_port: str,
    dep_time: str,
    arr_time: str,
    duration: int,
    airline: str,
    airplane: str,
) -> str:
    return f"{airline} {flight_no} - {dep_port} ({dep_time}) -> {arr_port} ({arr_time}) [{format_minutes(duration)}] - {airplane}"


def get_formatted_flights_info(flights: list) -> str:
    formatted_flights = []
    for flight in flights:
        for part in flight["flights"]:
            formatted_flights.append(
                format_one_flight(
                    part["flight_number"],
                    part["departure_airport"]["id"],
                    part["arrival_airport"]["id"],
                    part["departure_airport"]["time"],
                    part["arrival_airport"]["time"],
                    part["duration"],
                    part["airline"],
                    part["airplane"],
                )
            )
        if "layovers" in flight and len(flight["layovers"]) > 0:
            formatted_flights.append(
                f"Layover at {flight['layovers'][0]['id']}: {format_minutes(flight['layovers'][0]['duration'])}"
            )
        formatted_flights.append(
            f"Total Duration: {format_minutes(flight['total_duration'])}"
        )
        formatted_flights.append(f"Price (USD): ${flight['price']}")
        formatted_flights.append("")
    return "\n".join(formatted_flights)


def find_flights(
    departure_airport: str = Field(
        ..., description="The 3 letter departure airport code (IATA) e.g. LHR"
    ),
    arrival_airport: str = Field(
        ..., description="The 3 letter arrival airport code (IATA) e.g. JFK"
    ),
    departure_date: str = Field(
        ..., description="The departure date in the format YYYY-MM-DD"
    ),
    return_date: Optional[str] = Field(
        None, description="The return date in the format YYYY-MM-DD"
    ),
) -> str:
    """
    Find flights between two airports on given dates.
    """

    SERPAPI_KEY = os.getenv("SERPAPI_KEY")
    params = {
        "engine": "google_flights",
        "hl": "en",
        "departure_id": departure_airport,
        "arrival_id": arrival_airport,
        "outbound_date": departure_date,
        "return_date": return_date,
        "stops": 2,  # 1 stop of less
        "currency": "USD",
        "api_key": SERPAPI_KEY,
    }
    if return_date:
        params["type"] = "1"  # Round Trip (Default selection)
    else:
        params["type"] = "2"  # One Way

    try:
        print(f"\n> Finding flights from {departure_airport} to {arrival_airport}\n")
        search = GoogleSearch(params)
        results = search.get_dict()
        if "error" in results:
            raise ValueError(f"SerpAPI error: {results['error']}")
        flights_data = results.get("best_flights", [])
        first_line = f"Flights from {departure_airport} to {arrival_airport}:"
        return first_line + "\n\n" + get_formatted_flights_info(flights_data[:3])
    except Exception as e:
        raise Exception(f"Failed to search flights: {str(e)}")
