import heapq
import logging
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from ..models.domain import Flight, Hotel, TripPackage
from .cache import TravelCache
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ScoreFactors(Enum):
    PRICE_EFFICIENCY = "price_efficiency"
    FLIGHT_QUALITY = "flight_quality"
    HOTEL_RATING = "hotel_rating"
    DESTINATION_POPULARITY = "destination_popularity"

class TravelSearchEngine:
    def __init__(self, flights: List[Flight], hotels: List[Hotel]):
        self.flights = flights
        self.hotels = hotels
        self.cache = TravelCache()  # Initialize cache
        self.weight_config = {
            ScoreFactors.PRICE_EFFICIENCY: 0.4,
            ScoreFactors.FLIGHT_QUALITY: 0.25,
            ScoreFactors.HOTEL_RATING: 0.25,
            ScoreFactors.DESTINATION_POPULARITY: 0.1
        }
        logger.info(f"Initializing TravelSearchEngine with {len(flights)} flights and {len(hotels)} hotels")
        self._build_indexes()
    
    def _build_indexes(self):
        """Build indexes for faster searching"""
        self.flights_by_route = {}
        self.hotels_by_city = {}
        
        # Index flights
        for flight in self.flights:
            key = (flight.origin, flight.destination)
            if key not in self.flights_by_route:
                self.flights_by_route[key] = []
            self.flights_by_route[key].append(flight)
        
        # Log flight routes
        logger.debug(f"Built flight index with {len(self.flights_by_route)} routes")
        for (origin, dest), flights in self.flights_by_route.items():
            logger.debug(f"Route {origin}->{dest}: {len(flights)} flights")
        
        # Index hotels
        for hotel in self.hotels:
            if hotel.city_code not in self.hotels_by_city:
                self.hotels_by_city[hotel.city_code] = []
            self.hotels_by_city[hotel.city_code].append(hotel)
        
        # Log hotel distribution
        logger.debug(f"Built hotel index for {len(self.hotels_by_city)} cities")
    
    def _calculate_trip_score(self, trip: TripPackage, context: Dict[str, Any]) -> float:
        """Calculate a comprehensive score for a trip package"""
        scores = {}
        
        # Price Efficiency Score
        total_price = trip.total_cost  # Changed from total_price to total_cost
        avg_price = context.get('avg_price', total_price)
        price_ratio = 1 - (total_price / avg_price) if avg_price > 0 else 0
        scores[ScoreFactors.PRICE_EFFICIENCY] = max(0, min(1, price_ratio + 0.5))
        
        # Flight Quality Score (based on price and timing)
        outbound_score = 1 - (trip.outbound_flight.price / context.get('max_flight_price', trip.outbound_flight.price))
        return_score = 1 - (trip.return_flight.price / context.get('max_flight_price', trip.return_flight.price))
        scores[ScoreFactors.FLIGHT_QUALITY] = (outbound_score + return_score) / 2
        
        # Hotel Rating Score
        hotel_score = min(1.0, trip.hotel.rating / 5.0) if hasattr(trip.hotel, 'rating') else 0.5
        scores[ScoreFactors.HOTEL_RATING] = hotel_score
        
        # Destination Popularity Score (could be enhanced with actual data)
        dest_popularity = context.get('destination_popularity', {}).get(trip.destination, 0.5)
        scores[ScoreFactors.DESTINATION_POPULARITY] = dest_popularity
        
        # Calculate weighted score
        final_score = sum(scores[factor] * self.weight_config[factor] for factor in ScoreFactors)
        
        return final_score

    async def search_trips(self, origin: str, nights: int, budget: float, result_limit: int = 10) -> List[TripPackage]:
        # Use the cache decorator from instance
        @self.cache.cache_decorator(ttl=1800, prefix="search_trips")
        async def _cached_search():
            logger.info(f"Starting search: origin={origin}, nights={nights}, budget=${budget:.2f}, limit={result_limit}")
            
            top_trips = []
            entry_count = 0
            
            # Calculate context for scoring
            search_context = self._prepare_search_context(origin, budget)
            
            destinations = set(city for origin_, city in self.flights_by_route.keys() 
                             if origin_ == origin)
            logger.info(f"Found {len(destinations)} possible destinations from {origin}")
            
            for dest in destinations:
                outbound_flights = self.flights_by_route.get((origin, dest), [])
                return_flights = self.flights_by_route.get((dest, origin), [])
                dest_hotels = self.hotels_by_city.get(dest, [])
                
                if not (outbound_flights and return_flights and dest_hotels):
                    continue
                
                for combo in self._find_valid_combinations(outbound_flights, return_flights, 
                                                         dest_hotels, dest, nights, budget):
                    score = self._calculate_trip_score(combo, search_context)
                    entry = (-score, entry_count, combo)
                    entry_count += 1
                    
                    if len(top_trips) < result_limit:
                        heapq.heappush(top_trips, entry)
                    elif entry < top_trips[0]:
                        heapq.heapreplace(top_trips, entry)
            
            sorted_trips = [trip for _, _, trip in sorted(top_trips, key=lambda x: (-x[0], x[1]))]
            return sorted_trips

        # Call the cached function
        return await _cached_search()

    def _prepare_search_context(self, origin: str, budget: float) -> Dict[str, Any]:
        """Prepare context for trip scoring"""
        # Get all flight prices for normalization
        all_flights = [flight for flights in self.flights_by_route.values() for flight in flights]
        flight_prices = [f.price for f in all_flights]
        max_flight_price = max(flight_prices) if flight_prices else budget
        
        # Get all hotel prices for normalization
        all_hotels = [hotel for hotels in self.hotels_by_city.values() for hotel in hotels]
        hotel_prices = [h.price_per_night for h in all_hotels]
        max_hotel_price = max(hotel_prices) if hotel_prices else budget
        
        # Count routes per destination for popularity
        destination_popularity = {}
        for (orig, dest), flights in self.flights_by_route.items():
            if dest not in destination_popularity:
                destination_popularity[dest] = 0
            destination_popularity[dest] += len(flights)
        
        # Normalize destination popularity
        max_popularity = max(destination_popularity.values()) if destination_popularity else 1
        destination_popularity = {
            dest: count / max_popularity 
            for dest, count in destination_popularity.items()
        }
        
        return {
            'max_flight_price': max_flight_price,
            'max_hotel_price': max_hotel_price,
            'destination_popularity': destination_popularity,
            'avg_price': sum(flight_prices) / len(flight_prices) if flight_prices else budget
        }

    def _find_valid_combinations(self, outbound_flights: List[Flight], 
                               return_flights: List[Flight], 
                               hotels: List[Hotel], 
                               dest: str, 
                               nights: int, 
                               budget: float) -> List[TripPackage]:
        for hotel in hotels:
            hotel_cost = hotel.price_per_night * nights
            if hotel_cost >= budget:
                continue
            
            for outbound in outbound_flights:
                remaining_budget = budget - (hotel_cost + outbound.price)
                
                if remaining_budget <= 0:
                    continue
                
                for return_flight in (f for f in return_flights if f.price <= remaining_budget):
                    yield TripPackage(
                        destination=dest,
                        outbound_flight=outbound,
                        return_flight=return_flight,
                        hotel=hotel,
                        nights=nights
                    )

    def invalidate_cache(self):
        """Invalidate all cached search results"""
        try:
            self.cache.invalidate_pattern("search_trips:*")
            logger.info("Cache invalidated successfully")
        except Exception as e:
            logger.error(f"Failed to invalidate cache: {str(e)}")