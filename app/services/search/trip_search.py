import heapq
import logging
from typing import List, Dict, Any
from ...models.domain import TripPackage
from ..cache import TravelCache
from .criteria import SearchCriteria
from .index_manager import TravelIndexManager
from ..scoring.trip_scorer import TripScorer
from .criteria import SearchCriteria


logger = logging.getLogger(__name__)

class TripSearch:
    def __init__(
        self, 
        index_manager: TravelIndexManager,
        scorer: TripScorer,
        cache: TravelCache
    ):
        self.indexes = index_manager
        self.scorer = scorer
        self.cache = cache

    async def search(self, criteria: SearchCriteria) -> List[TripPackage]:
        @self.cache.cache_decorator(ttl=1800, prefix="search_trips")
        async def _cached_search(criteria: SearchCriteria):
            logger.info(
                f"Starting search: origin={criteria.origin}, "
                f"nights={criteria.nights}, budget=${criteria.budget:.2f}"
            )

            context = self._prepare_search_context(criteria)
            top_trips = []
            entry_count = 0

            destinations = set(
                city for origin_, city in self.indexes.flights_by_route.keys()
                if origin_ == criteria.origin
            )

            for dest in destinations:
                for combo in self._generate_combinations(criteria, dest):
                    score = self.scorer.calculate_score(combo, context)
                    combo.score = score
                    entry = (-score, entry_count, combo)
                    entry_count += 1

                    if len(top_trips) < criteria.result_limit:
                        heapq.heappush(top_trips, entry)
                    elif entry < top_trips[0]:
                        heapq.heapreplace(top_trips, entry)

            return [
                trip for _, _, trip in sorted(top_trips, key=lambda x: (-x[0], x[1]))
            ]

        return await _cached_search(criteria)

    def _prepare_search_context(self, criteria: SearchCriteria) -> Dict[str, Any]:
        flight_prices = [
            f.price for flights in self.indexes.flights_by_route.values()
            for f in flights
        ]
        hotel_prices = [
            h.price_per_night 
            for hotels in self.indexes.hotels_by_city.values()
            for h in hotels
        ]

        return {
            "max_flight_price": max(flight_prices) if flight_prices else criteria.budget,
            "max_hotel_price": max(hotel_prices) if hotel_prices else criteria.budget,
            "destination_popularity": self.indexes.destination_popularity,
            "avg_price": (
                sum(flight_prices) / len(flight_prices)
                if flight_prices else criteria.budget
            ),
        }

    def _generate_combinations(
        self, criteria: SearchCriteria, dest: str
    ) -> List[TripPackage]:
        outbound_flights = self.indexes.flights_by_route.get(
            (criteria.origin, dest), []
        )
        return_flights = self.indexes.flights_by_route.get(
            (dest, criteria.origin), []
        )
        hotels = self.indexes.hotels_by_city.get(dest, [])

        for hotel in hotels:
            if (criteria.min_hotel_rating and 
                hotel.rating < criteria.min_hotel_rating):
                continue

            hotel_cost = hotel.price_per_night * criteria.nights
            if hotel_cost >= criteria.budget:
                continue

            for outbound in outbound_flights:
                if (criteria.max_stops is not None and 
                    len(outbound.stops) > criteria.max_stops):
                    continue

                remaining_budget = criteria.budget - (hotel_cost + outbound.price)
                if remaining_budget <= 0:
                    continue

                for return_flight in return_flights:
                    if (criteria.max_stops is not None and 
                        len(return_flight.stops) > criteria.max_stops):
                        continue

                    if return_flight.price <= remaining_budget:
                        yield TripPackage(
                            destination=dest,
                            outbound_flight=outbound,
                            return_flight=return_flight,
                            hotel=hotel,
                            nights=criteria.nights,
                        )
