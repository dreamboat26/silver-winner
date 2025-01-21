from typing import Any

from llama_index.core.llms.llm import LLM
from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
)
import gh_md_to_html
import pdfkit

from tools.flights import find_flights
from tools.hotels import find_hotels
from tools.places import find_places_to_visit

from agents.deligator import extract_tour_information
from agents.itinerary_writer import write_itinerary


class GotDataForFlights(Event):
    city_from: str
    city_to: str
    departure_date: str
    return_date: str


class GotTourPlanningRequest(Event):
    city: str


class GotHotelsData(Event):
    city: str
    check_in_date: str
    check_out_date: str


class FetchedFlightsData(Event):
    flights_info: str


class FetchedPlacesToVisit(Event):
    places_info: str


class FetchedHotelsData(Event):
    hotels_info: str


class TourPlannerWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.llm = llm

    @step
    async def deligate_tasks(
        self, ctx: Context, ev: StartEvent
    ) -> GotDataForFlights | GotHotelsData | GotTourPlanningRequest | StopEvent:
        query = ev.query
        await ctx.set("query", query)
        extracted_info = await extract_tour_information(query, self.llm)
        if not extracted_info.tour_info:
            return StopEvent(
                result=f"Failed to plan the tour. Possible reason: {extracted_info.reasoning}"
            )
        await ctx.set("destination", extracted_info.tour_info.destination)
        ctx.send_event(
            GotDataForFlights(
                city_from=extracted_info.tour_info.airport_from,
                city_to=extracted_info.tour_info.airport_to,
                return_date=extracted_info.tour_info.return_date,
                departure_date=extracted_info.tour_info.departure_date,
            )
        )
        ctx.send_event(
            GotTourPlanningRequest(
                city=extracted_info.tour_info.destination,
            )
        )
        ctx.send_event(
            GotHotelsData(
                city=extracted_info.tour_info.destination,
                check_in_date=extracted_info.tour_info.departure_date,
                check_out_date=extracted_info.tour_info.return_date,
            )
        )

    @step
    async def find_flights_step(self, ev: GotDataForFlights) -> FetchedFlightsData:
        flights_info = find_flights(
            ev.city_from, ev.city_to, ev.departure_date, ev.return_date
        )
        return FetchedFlightsData(flights_info=flights_info)

    @step
    async def find_hotels_step(self, ev: GotHotelsData) -> FetchedHotelsData:
        hotels_info = find_hotels(ev.city, ev.check_in_date, ev.check_out_date)
        return FetchedHotelsData(hotels_info=hotels_info)

    @step
    async def find_sights_step(
        self, ev: GotTourPlanningRequest
    ) -> FetchedPlacesToVisit:
        sights_info = find_places_to_visit(ev.city)
        return FetchedPlacesToVisit(places_info=sights_info)

    @step
    async def print_itinerary(
        self,
        ctx: Context,
        ev: FetchedFlightsData | FetchedHotelsData | FetchedPlacesToVisit,
    ) -> StopEvent:
        query = await ctx.get("query")
        destination = await ctx.get("destination")
        events = ctx.collect_events(
            ev, [FetchedFlightsData, FetchedHotelsData, FetchedPlacesToVisit]
        )
        if events is None:
            return None

        flights_ev, hotels_ev, places_ev = events
        itinerary = await write_itinerary(
            query,
            destination,
            flights_info=flights_ev.flights_info,
            hotels_info=hotels_ev.hotels_info,
            sights_info=places_ev.places_info,
            llm=self.llm,
        )
        md_file = "itinerary.md"
        pdf_file = "itinerary.pdf"
        with open(md_file, "w") as f:
            f.write(itinerary)
        try:
            pdfkit.from_string(
                gh_md_to_html.markdown_to_html_via_github_api(itinerary), pdf_file
            )
        except Exception as e:
            pass
        print("\n> Done planning tour! Trying to open the itinerary...\n")
        return StopEvent(result=pdf_file)
