import heapq
import logging
from typing import List, Dict, Any
from ..models.domain import Flight, Hotel, TripPackage
from .cache import TravelCache
from enum import Enum
from ..config.config import (
    SCORE_WEIGHTS,
    FLIGHT_TIME_SCORES,
    FLIGHT_HOURS,
    STOP_PENALTY,
    HOTEL_SCORE_FACTORS
)

logger = logging.getLogger(__name__)


class ScoreFactors(Enum):
    """Enumeration of factors used in trip scoring."""

    PRICE_EFFICIENCY = "price_efficiency"
    FLIGHT_QUALITY = "flight_quality"
    HOTEL_RATING = "hotel_rating"
    DESTINATION_POPULARITY = "destination_popularity"


class TravelSearchEngine:
    """
    Core search engine for finding and scoring travel combinations.

    Attributes:
        flights (List[Flight]): Available flights
        hotels (List[Hotel]): Available hotels
        cache (TravelCache): Caching mechanism for search results
        weight_config (Dict): Configuration for scoring weights
    """

    def __init__(self, flights: List[Flight], hotels: List[Hotel]):
        """
        Initialize the search engine with available flights and hotels.

        Args:
            flights: List of available Flight objects
            hotels: List of available Hotel objects
        """
        self.flights = flights
        self.hotels = hotels
        self.cache = TravelCache()
        self.weight_config = {
            ScoreFactors.PRICE_EFFICIENCY: 0.4,
            ScoreFactors.FLIGHT_QUALITY: 0.25,
            ScoreFactors.HOTEL_RATING: 0.25,
            ScoreFactors.DESTINATION_POPULARITY: 0.1,
        }
        logger.info(
            f"Initializing TravelSearchEngine with {len(flights)} flights and {len(hotels)} hotels"
        )
        self._build_indexes()

    def _build_indexes(self):
        """
        Build internal indexes for faster searching.
        Creates flight route and hotel city indexes.
        """
        self.flights_by_route = {}
        self.hotels_by_city = {}

        # Index flights
        for flight in self.flights:
            key = (flight.origin, flight.destination)
            if key not in self.flights_by_route:
                self.flights_by_route[key] = []
            self.flights_by_route[key].append(flight)

        logger.debug(f"Built flight index with {len(self.flights_by_route)} routes")

        # Index hotels
        for hotel in self.hotels:
            if hotel.city_code not in self.hotels_by_city:
                self.hotels_by_city[hotel.city_code] = []
            self.hotels_by_city[hotel.city_code].append(hotel)

        logger.debug(f"Built hotel index for {len(self.hotels_by_city)} cities")

    def _calculate_trip_score(self, trip: TripPackage, search_context: Dict) -> float:
        total_cost = (
            trip.outbound_flight.price + 
            trip.return_flight.price + 
            trip.hotel.price_per_night * trip.nights
        )

        # Price score (0-100)
        max_cost = search_context['max_flight_price'] * 2 + search_context['max_hotel_price'] * trip.nights
        price_score = max(0, 100 * (1 - (total_cost / max_cost))) * 1.5  # Amplify price differences

        def get_flight_score(flight) -> float:
            hour = flight.departure_time.hour
            
            # Base time score (0-100)
            if 8 <= hour <= 11:  # Prime time
                time_score = 100
            elif 11 < hour <= 16:  # Good business hours
                time_score = 80
            elif 6 <= hour < 8:  # Early morning
                time_score = 60
            elif 16 < hour <= 21:  # Evening
                time_score = 50
            else:  # Red-eye/late night
                time_score = 20
            
            # Stops penalty
            stops_penalty = len(flight.stops) * 40
            return max(0, time_score - stops_penalty)

        outbound_score = get_flight_score(trip.outbound_flight)
        return_score = get_flight_score(trip.return_flight)
        flight_score = (outbound_score + return_score) / 2

        # Hotel score (0-100)
        hotel_score = min(100, (
            (trip.hotel.stars * 18) +  # Increased weight for stars
            (trip.hotel.rating * 10) +  # Increased weight for rating
            (len(trip.hotel.amenities) * 7)  # Increased weight for amenities
        ))

        weighted_score = (
            price_score * 0.35 +
            flight_score * 0.40 +
            hotel_score * 0.20 +
            search_context['destination_popularity'].get(trip.destination, 0) * 100 * 0.05
        )

        # Final normalization to ensure 0-100 range
        final_score = weighted_score * 1.2  # Scale up final score
        return round(max(0, min(100, final_score)), 2)

    
    async def search_trips(
        self, origin: str, nights: int, budget: float, result_limit: int = 10
    ) -> List[TripPackage]:
        """
        Search for trip packages matching the given criteria.

        Args:
            origin: Origin airport code
            nights: Number of nights to stay
            budget: Maximum total budget
            result_limit: Maximum number of results to return

        Returns:
            List[TripPackage]: Sorted list of trip packages
        """

        @self.cache.cache_decorator(ttl=1800, prefix="search_trips")
        async def _cached_search():
            logger.info(
                f"Starting search: origin={origin}, nights={nights}, budget=${budget:.2f}"
            )

            top_trips = []
            entry_count = 0
            search_context = self._prepare_search_context(origin, budget)

            destinations = set(
                city
                for origin_, city in self.flights_by_route.keys()
                if origin_ == origin
            )

            for dest in destinations:
                for combo in self._find_valid_combinations(
                    self.flights_by_route.get((origin, dest), []),
                    self.flights_by_route.get((dest, origin), []),
                    self.hotels_by_city.get(dest, []),
                    dest,
                    nights,
                    budget,
                ):
                    score = self._calculate_trip_score(combo, search_context)
                    combo.score = score 
                    entry = (-score, entry_count, combo)
                    entry_count += 1

                    if len(top_trips) < result_limit:
                        heapq.heappush(top_trips, entry)
                    elif entry < top_trips[0]:
                        heapq.heapreplace(top_trips, entry)

            return [
                trip for _, _, trip in sorted(top_trips, key=lambda x: (-x[0], x[1]))
            ]

        return await _cached_search()

    def _prepare_search_context(self, origin: str, budget: float) -> Dict[str, Any]:
        """
        Prepare context data for trip scoring.

        Args:
            origin: Origin airport code
            budget: Maximum budget

        Returns:
            Dict containing context data for scoring calculations
        """
        # Get all flight prices for normalization
        all_flights = [
            flight for flights in self.flights_by_route.values() for flight in flights
        ]
        flight_prices = [f.price for f in all_flights]
        max_flight_price = max(flight_prices) if flight_prices else budget

        # Get all hotel prices for normalization
        all_hotels = [
            hotel for hotels in self.hotels_by_city.values() for hotel in hotels
        ]
        hotel_prices = [h.price_per_night for h in all_hotels]
        max_hotel_price = max(hotel_prices) if hotel_prices else budget

        # Count routes per destination for popularity
        destination_popularity = {}
        for (orig, dest), flights in self.flights_by_route.items():
            if dest not in destination_popularity:
                destination_popularity[dest] = 0
            destination_popularity[dest] += len(flights)

        # Normalize destination popularity
        max_popularity = (
            max(destination_popularity.values()) if destination_popularity else 1
        )
        destination_popularity = {
            dest: count / max_popularity
            for dest, count in destination_popularity.items()
        }

        return {
            "max_flight_price": max_flight_price,
            "max_hotel_price": max_hotel_price,
            "destination_popularity": destination_popularity,
            "avg_price": (
                sum(flight_prices) / len(flight_prices) if flight_prices else budget
            ),
        }

    def _find_valid_combinations(
        self,
        outbound_flights: List[Flight],
        return_flights: List[Flight],
        hotels: List[Hotel],
        dest: str,
        nights: int,
        budget: float,
    ) -> List[TripPackage]:
        """
        Generate valid flight and hotel combinations within budget.

        Args:
            outbound_flights: List of outbound flights
            return_flights: List of return flights
            hotels: List of hotels at destination
            dest: Destination airport code
            nights: Number of nights
            budget: Maximum budget

        Yields:
            TripPackage: Valid trip combinations
        """
        for hotel in hotels:
            hotel_cost = hotel.price_per_night * nights
            if hotel_cost >= budget:
                continue

            for outbound in outbound_flights:
                remaining_budget = budget - (hotel_cost + outbound.price)

                if remaining_budget <= 0:
                    continue

                for return_flight in (
                    f for f in return_flights if f.price <= remaining_budget
                ):
                    yield TripPackage(
                        destination=dest,
                        outbound_flight=outbound,
                        return_flight=return_flight,
                        hotel=hotel,
                        nights=nights,
                    )

    def invalidate_cache(self):
        """Invalidate all cached search results."""
        try:
            self.cache.invalidate_pattern("search_trips:*")
            logger.info("Cache invalidated successfully")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {str(e)}")
