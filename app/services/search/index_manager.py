from typing import Dict, List, Tuple
from ...models.domain import Flight, Hotel

class TravelIndexManager:
    def __init__(self, flights: List[Flight], hotels: List[Hotel]):
        self.flights_by_route = self._index_flights(flights)
        self.hotels_by_city = self._index_hotels(hotels)
        self._compute_destination_stats()

    def _index_flights(self, flights: List[Flight]) -> Dict[Tuple[str, str], List[Flight]]:
        indexed = {}
        for flight in flights:
            key = (flight.origin, flight.destination)
            if key not in indexed:
                indexed[key] = []
            indexed[key].append(flight)
        return indexed

    def _index_hotels(self, hotels: List[Hotel]) -> Dict[str, List[Hotel]]:
        indexed = {}
        for hotel in hotels:
            if hotel.city_code not in indexed:
                indexed[hotel.city_code] = []
            indexed[hotel.city_code].append(hotel)
        return indexed

    def _compute_destination_stats(self):
        self.destination_popularity = {}
        for (_, dest), flights in self.flights_by_route.items():
            if dest not in self.destination_popularity:
                self.destination_popularity[dest] = 0
            self.destination_popularity[dest] += len(flights)
        
        max_popularity = max(self.destination_popularity.values()) if self.destination_popularity else 1
        self.destination_popularity = {
            dest: count / max_popularity
            for dest, count in self.destination_popularity.items()
        }
