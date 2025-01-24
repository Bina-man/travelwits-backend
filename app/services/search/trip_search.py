from collections import deque
import heapq
import logging
from typing import List, Dict, Any
from ...models.domain import Hotel, TripPackage, Flight
from ..cache import TravelCache
from .criteria import SearchCriteria
from .index_manager import TravelIndexManager
from ..scoring.trip_scorer import TripScorer
from .criteria import SearchCriteria
from ...config.config import DEFAULT_CACHE_TTL


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
        @self.cache.cache_decorator(ttl=DEFAULT_CACHE_TTL, prefix="search_trips")
        async def _cached_search(criteria: SearchCriteria):
            logger.info(f"Starting search: origin={criteria.origin}, nights={criteria.nights}, budget=${criteria.budget:.2f}")
            context = self._prepare_search_context(criteria)
            top_trips = []
            entry_count = 0

            destinations = set(city for origin_, city in self.indexes.flights_by_route.keys() if origin_ == criteria.origin)

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

            return [trip for _, _, trip in sorted(top_trips, key=lambda x: (-x[0], x[1]))]

        return await _cached_search(criteria)

    def _prepare_search_context(self, criteria: SearchCriteria) -> Dict[str, Any]:
        flight_prices = [f.price for flights in self.indexes.flights_by_route.values() for f in flights]
        hotel_prices = [h.price_per_night for hotels in self.indexes.hotels_by_city.values() for h in hotels]

        return {
            "max_flight_price": max(flight_prices) if flight_prices else criteria.budget,
            "max_hotel_price": max(hotel_prices) if hotel_prices else criteria.budget,
            "destination_popularity": self.indexes.destination_popularity,
            "avg_price": sum(flight_prices) / len(flight_prices) if flight_prices else criteria.budget,
        }

    def _generate_combinations(self, criteria: SearchCriteria, dest: str) -> List[TripPackage]:
        seen_combinations = set()
        valid_combinations = []
        
        def find_routes(origin: str, final_dest: str, visited: set, current_path: list, cost: float) -> List[List[Flight]]:
            if cost > criteria.budget:
                return []
                
            if origin == final_dest and current_path:  # Check path not empty
                return [current_path]
                
            routes = []
            for next_dest, flights in self.indexes.flights_by_route.items():
                if next_dest[0] == origin and next_dest[1] not in visited:
                    for flight in flights:
                        if cost + flight.price <= criteria.budget:
                            new_visited = visited | {next_dest[1]}
                            new_paths = find_routes(
                                next_dest[1], 
                                final_dest, 
                                new_visited,
                                current_path + [flight],
                                cost + flight.price
                            )
                            routes.extend(new_paths)
            return routes
        
        def find_routes_bfs(origin: str, final_dest: str) -> List[List[Flight]]:
            queue = deque([(origin, [], 0)])  # (city, path, cost)
            routes = []
            visited = set([origin])
            
            while queue:
                current_city, path, cost = queue.popleft()
                
                if current_city == final_dest and path:
                    routes.append(path)
                    continue
                    
                for next_dest, flights in self.indexes.flights_by_route.items():
                    if next_dest[0] == current_city and next_dest[1] not in visited:
                        for flight in flights:
                            new_cost = cost + flight.price
                            if new_cost <= criteria.budget:
                                visited.add(next_dest[1])
                                queue.append((next_dest[1], path + [flight], new_cost))
                                
            return routes

        # outbound_routes = find_routes_bfs(criteria.origin, dest) BFS for shortest path
        # return_routes = find_routes_bfs(dest, criteria.origin) BFS for shortest path
        
        outbound_routes = find_routes(criteria.origin, dest, {criteria.origin}, [], 0) # DFS for all paths for varied outputs
        return_routes = find_routes(dest, criteria.origin, {dest}, [], 0) # DFS for all paths for varied outputs

        hotels = self._filter_valid_hotels(
            self.indexes.hotels_by_city.get(dest, []),
            criteria.budget,
            criteria.nights
        )

        for hotel in hotels:
            if criteria.min_hotel_rating and hotel.rating < criteria.min_hotel_rating:
                continue

            hotel_cost = hotel.price_per_night * criteria.nights
            
            for outbound_path in outbound_routes:
                outbound_cost = sum(f.price for f in outbound_path)
                if outbound_cost + hotel_cost > criteria.budget:
                    continue
                    
                for return_path in return_routes:
                    total_cost = outbound_cost + sum(f.price for f in return_path) + hotel_cost
                    if total_cost > criteria.budget:
                        continue

                    if criteria.max_stops is not None:
                        total_stops = sum(len(f.stops) for f in outbound_path + return_path)
                        if total_stops > criteria.max_stops:
                            continue

                    trip = TripPackage(
                        destination=dest,
                        outbound_flight=outbound_path[0],  # First flight of path
                        return_flight=return_path[0],      # First flight of path 
                        hotel=hotel,
                        nights=criteria.nights,
                        total_cost=total_cost,
                        outbound_path=outbound_path,       # Add full paths
                        return_path=return_path
                    )

                    combo_key = f"{'-'.join(f.id for f in outbound_path)}_{'-'.join(f.id for f in return_path)}_{hotel.id}"
                    if combo_key not in seen_combinations:
                        seen_combinations.add(combo_key)
                        trip.score = self.scorer.calculate_score(trip, self._prepare_search_context(criteria))
                        valid_combinations.append(trip)

        return valid_combinations

    def _filter_valid_hotels(self, hotels: List[Hotel], budget: float, nights: int) -> List[Hotel]:
        return [hotel for hotel in hotels if hotel.price_per_night * nights <= budget]
    
    def _calculate_total_cost(self, trip: TripPackage) -> float:
        return trip.outbound_flight.price + trip.return_flight.price + trip.hotel.price_per_night * trip.nights

    def _is_within_budget(self, trip: TripPackage, budget: float) -> bool:
        return self._calculate_total_cost(trip) <= budget