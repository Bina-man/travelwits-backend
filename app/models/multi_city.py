# models/multi_city.py
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import heapq

from app.models.domain import Hotel

@dataclass
class MultiCityFlight:
    id: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    stops: List[str]

@dataclass
class MultiCityStay:
    city: str
    arrival_flight: MultiCityFlight
    hotel: Optional['Hotel']  # Optional for last city if no stay needed
    nights: int
    
    @property
    def cost(self) -> float:
        hotel_cost = self.hotel.price_per_night * self.nights if self.hotel else 0
        return self.arrival_flight.price + hotel_cost

class MultiCityTripNode:
    def __init__(self, 
                 city: str, 
                 remaining_budget: float,
                 cumulative_score: float = 0,
                 parent: Optional['MultiCityTripNode'] = None):
        self.city = city
        self.remaining_budget = remaining_budget
        self.cumulative_score = cumulative_score
        self.parent = parent
        self.stays: List[MultiCityStay] = []
        self.children: Dict[str, 'MultiCityTripNode'] = {}
        
    def add_stay(self, flight: MultiCityFlight, hotel: Optional[Hotel], nights: int) -> bool:
        """Adds a stay at the current city"""
        stay_cost = flight.price + (hotel.price_per_night * nights if hotel else 0)
        if stay_cost <= self.remaining_budget:
            stay = MultiCityStay(self.city, flight, hotel, nights)
            self.stays.append(stay)
            return True
        return False
    
    def add_next_city(self, city: str, stay: MultiCityStay) -> Optional['MultiCityTripNode']:
        """Adds a new city to visit next"""
        if city not in self.children:
            new_budget = self.remaining_budget - stay.cost
            if new_budget > 0:
                # Calculate score for this leg of the journey
                leg_score = self._calculate_leg_score(stay)
                new_cumulative_score = self.cumulative_score + leg_score
                
                node = MultiCityTripNode(
                    city=city,
                    remaining_budget=new_budget,
                    cumulative_score=new_cumulative_score,
                    parent=self
                )
                self.children[city] = node
                return node
        return None
    
    def _calculate_leg_score(self, stay: MultiCityStay) -> float:
        """Calculate score for this particular leg of the journey"""
        # Price score (lower price = higher score)
        price_score = 1000 / stay.cost if stay.cost > 0 else 0
        
        # Flight convenience score
        flight_score = 10.0 - len(stay.arrival_flight.stops) * 2
        if 8 <= stay.arrival_flight.departure_time.hour <= 20:
            flight_score += 2
        
        # Hotel score (if applicable)
        hotel_score = 0
        if stay.hotel:
            hotel_score = stay.hotel.rating * stay.hotel.stars + len(stay.hotel.amenities) * 0.5
        
        # Weighted combination
        weights = {'price': 0.4, 'flight': 0.3, 'hotel': 0.3}
        return (price_score * weights['price'] + 
                flight_score * weights['flight'] + 
                hotel_score * weights['hotel'])

class MultiCitySearchEngine:
    def __init__(self, flights: List[MultiCityFlight], hotels: Dict[str, List[Hotel]]):
        self.flights = flights
        self.hotels = hotels
        self._build_indexes()
    
    def _build_indexes(self):
        """Build indexes for faster searching"""
        self.flights_by_origin = {}
        for flight in self.flights:
            if flight.origin not in self.flights_by_origin:
                self.flights_by_origin[flight.origin] = []
            self.flights_by_origin[flight.origin].append(flight)
    
    def search_multi_city_trips(self, 
                              origin: str, 
                              must_visit_cities: List[str],
                              optional_cities: List[str],
                              total_nights: int,
                              budget: float,
                              max_results: int = 5) -> List[List[MultiCityStay]]:
        """
        Search for multi-city trips with required and optional cities
        Returns top N trips sorted by cumulative score
        """
        root = MultiCityTripNode(origin, budget)
        top_trips = []  # Will store (score, trip) tuples
        
        def build_trip_tree(node: MultiCityTripNode, 
                          remaining_cities: List[str],
                          remaining_nights: int,
                          path: List[MultiCityStay] = None):
            if path is None:
                path = []
            
            # Base case: check if we've visited all required cities
            if not any(city in must_visit_cities for city in remaining_cities):
                # Valid trip found - add to results
                trip_score = node.cumulative_score
                if len(top_trips) < max_results:
                    heapq.heappush(top_trips, (trip_score, path.copy()))
                elif trip_score > top_trips[0][0]:
                    heapq.heapreplace(top_trips, (trip_score, path.copy()))
                return
            
            # Get available flights from current city
            available_flights = self.flights_by_origin.get(node.city, [])
            
            for flight in available_flights:
                if flight.destination not in remaining_cities:
                    continue
                
                # Try different lengths of stay
                for nights in range(1, min(remaining_nights - len(remaining_cities) + 2, 5)):
                    # Get available hotels
                    city_hotels = self.hotels.get(flight.destination, [])
                    for hotel in city_hotels:
                        # Create a stay
                        stay = MultiCityStay(flight.destination, flight, hotel, nights)
                        if stay.cost <= node.remaining_budget:
                            # Try adding this stay
                            next_node = node.add_next_city(flight.destination, stay)
                            if next_node:
                                new_remaining = [c for c in remaining_cities 
                                              if c != flight.destination]
                                new_path = path + [stay]
                                
                                # Recurse
                                build_trip_tree(next_node, 
                                             new_remaining,
                                             remaining_nights - nights,
                                             new_path)
        
        # Start the search
        all_cities = must_visit_cities + optional_cities
        build_trip_tree(root, all_cities, total_nights)
        
        # Return sorted results
        return [trip for _, trip in sorted(top_trips, key=lambda x: x[0], reverse=True)]