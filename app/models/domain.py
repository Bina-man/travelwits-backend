from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

class TravelClass(Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"

class Airport(BaseModel):
    code: str = Field(..., min_length=3, max_length=3)
    city: str
    timezone: str

class Flight(BaseModel):
    id: str
    origin: str = Field(..., min_length=3, max_length=3)
    destination: str = Field(..., min_length=3, max_length=3)
    departure_time: datetime
    arrival_time: datetime
    price: float = Field(..., gt=0)
    stops: List[str] = []

    @property
    def duration(self) -> timedelta:
        return self.arrival_time - self.departure_time

    @property
    def is_direct(self) -> bool:
        return len(self.stops) == 0

class Hotel(BaseModel):
    id: str
    name: str
    city_code: str = Field(..., min_length=3, max_length=3)
    stars: int = Field(..., ge=1, le=5)
    rating: float = Field(..., ge=0, le=5)
    price_per_night: float = Field(..., gt=0)
    amenities: List[str]

class TripPackage(BaseModel):
    score: Optional[float] = None
    destination: str = Field(..., min_length=3, max_length=3)
    outbound_flight: Flight
    return_flight: Flight
    hotel: Hotel
    nights: int = Field(..., ge=1, le=30)

    @property
    def total_cost(self) -> float:
        return (self.outbound_flight.price + 
                self.return_flight.price + 
                self.hotel.price_per_night * self.nights)

    def calculate_score(self) -> float:
        weights = {'price': 0.35, 'comfort': 0.35, 'convenience': 0.30}
        return sum(score * weight for score, weight in zip(
            [self._calculate_price_score(),
             self._calculate_comfort_score(),
             self._calculate_convenience_score()],
            weights.values()
        ))

    def _calculate_price_score(self) -> float:
        return 1000 / (self.total_cost / self.nights)

    def _calculate_comfort_score(self) -> float:
        return self.hotel.rating * self.hotel.stars + len(self.hotel.amenities) * 0.5

    def _calculate_convenience_score(self) -> float:
        score = 10.0 - len(self.outbound_flight.stops) * 2 - len(self.return_flight.stops) * 2
        if 8 <= self.outbound_flight.departure_time.hour <= 20:
            score += 2
        return max(score, 0)