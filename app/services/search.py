import heapq
import logging
from typing import List
from ..models.domain import Flight, Hotel, TripPackage

logger = logging.getLogger(__name__)

class TravelSearchEngine:
    def __init__(self, flights: List[Flight], hotels: List[Hotel]):
        self.flights = flights
        self.hotels = hotels
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
            logger.debug(f"Route {origin}->{dest}: {len(flights)} flights, "
                        f"Price range: ${min(f.price for f in flights):.2f}-${max(f.price for f in flights):.2f}")
        
        # Index hotels
        for hotel in self.hotels:
            if hotel.city_code not in self.hotels_by_city:
                self.hotels_by_city[hotel.city_code] = []
            self.hotels_by_city[hotel.city_code].append(hotel)
        
        # Log hotel distribution
        logger.debug(f"Built hotel index for {len(self.hotels_by_city)} cities")
        for city, hotels in self.hotels_by_city.items():
            logger.debug(f"City {city}: {len(hotels)} hotels, "
                        f"Price range: ${min(h.price_per_night for h in hotels):.2f}-${max(h.price_per_night for h in hotels):.2f}/night")
    
    def search_trips(self, origin: str, nights: int, budget: float, result_limit: int = 10) -> List[TripPackage]:
        logger.info(f"Starting search: origin={origin}, nights={nights}, budget=${budget:.2f}, limit={result_limit}")
        
        top_trips = []
        entry_count = 0
        
        destinations = set(city for origin_, city in self.flights_by_route.keys() 
                         if origin_ == origin)
        logger.info(f"Found {len(destinations)} possible destinations from {origin}: {destinations}")
        
        for dest in destinations:
            outbound_flights = self.flights_by_route.get((origin, dest), [])
            return_flights = self.flights_by_route.get((dest, origin), [])
            dest_hotels = self.hotels_by_city.get(dest, [])
            
            logger.debug(f"Checking destination {dest}:")
            logger.debug(f"  - Outbound flights: {len(outbound_flights)}")
            logger.debug(f"  - Return flights: {len(return_flights)}")
            logger.debug(f"  - Hotels: {len(dest_hotels)}")
            
            if not (outbound_flights and return_flights and dest_hotels):
                logger.warning(f"Skipping {dest} - missing required components")
                continue
                
            valid_combinations = 0
            for combo in self._find_valid_combinations(outbound_flights, return_flights, 
                                                     dest_hotels, dest, nights, budget):
                valid_combinations += 1
                score = combo.calculate_score()
                entry = (-score, entry_count, combo)
                entry_count += 1
                
                if len(top_trips) < result_limit:
                    heapq.heappush(top_trips, entry)
                elif entry < top_trips[0]:
                    heapq.heapreplace(top_trips, entry)
            
            logger.debug(f"Found {valid_combinations} valid combinations for {dest}")
        
        sorted_trips = [trip for _, _, trip in sorted(top_trips, key=lambda x: (-x[0], x[1]))]
        logger.info(f"Search complete. Returning {len(sorted_trips)} trips")
        return sorted_trips
    
    def _find_valid_combinations(self, outbound_flights: List[Flight], 
                               return_flights: List[Flight], 
                               hotels: List[Hotel], 
                               dest: str, 
                               nights: int, 
                               budget: float) -> List[TripPackage]:
        combinations_checked = 0
        budget_exceeded = 0
        
        for hotel in hotels:
            hotel_cost = hotel.price_per_night * nights
            if hotel_cost >= budget:
                budget_exceeded += 1
                continue
            
            for outbound in outbound_flights:
                remaining_budget = budget - (hotel_cost + outbound.price)
                combinations_checked += 1
                
                if remaining_budget <= 0:
                    budget_exceeded += 1
                    continue
                
                for return_flight in (f for f in return_flights if f.price <= remaining_budget):
                    yield TripPackage(
                        destination=dest,
                        outbound_flight=outbound,
                        return_flight=return_flight,
                        hotel=hotel,
                        nights=nights
                    )
        
        logger.debug(f"Combinations stats for {dest}:")
        logger.debug(f"  - Total checked: {combinations_checked}")
        logger.debug(f"  - Budget exceeded: {budget_exceeded}")