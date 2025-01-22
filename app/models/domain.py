from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List
from enum import Enum

class TravelClass(Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"

@dataclass
class Airport:
    code: str
    city: str
    timezone: str

@dataclass
class Flight:
    id: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    stops: List[str]
    
    @property
    def duration(self) -> timedelta:
        return self.arrival_time - self.departure_time
    
    @property
    def is_direct(self) -> bool:
        return len(self.stops) == 0

@dataclass
class Hotel:
    id: str
    name: str
    city_code: str
    stars: int
    rating: float
    price_per_night: float
    amenities: List[str]

@dataclass
class TripPackage:
    destination: str
    outbound_flight: Flight
    return_flight: Flight
    hotel: Hotel
    nights: int
    
    @property
    def total_cost(self) -> float:
        return (self.outbound_flight.price + 
                self.return_flight.price + 
                self.hotel.price_per_night * self.nights)
    
    def calculate_score(self) -> float:
        """Calculate a comprehensive score for the trip package"""
        price_score = self._calculate_price_score()
        comfort_score = self._calculate_comfort_score()
        convenience_score = self._calculate_convenience_score()
        
        weights = {
            'price': 0.35,
            'comfort': 0.35,
            'convenience': 0.30
        }
        
        return (price_score * weights['price'] +
                comfort_score * weights['comfort'] +
                convenience_score * weights['convenience'])
    
    def _calculate_price_score(self) -> float:
        return 1000 / (self.total_cost / self.nights)

    def _calculate_comfort_score(self) -> float:
        return self.hotel.rating * self.hotel.stars + len(self.hotel.amenities) * 0.5

    def _calculate_convenience_score(self) -> float:
        score = 10.0 - len(self.outbound_flight.stops) * 2 - len(self.return_flight.stops) * 2
        if 8 <= self.outbound_flight.departure_time.hour <= 20:
            score += 2
        return max(score, 0)