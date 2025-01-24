from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum
from ..config.config import MIN_NIGHTS, MAX_NIGHTS,SCORING_WEIGHTS, AIRPORT_CODE_LENGTH, MIN_CUSTOMER_SPENDING, HOTEL_STAY
class TravelClass(Enum):
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"

class Airport(BaseModel):
    code: str = Field(..., min_length=AIRPORT_CODE_LENGTH, max_length=AIRPORT_CODE_LENGTH)
    city: str
    timezone: str

class Flight(BaseModel):
    id: str
    origin: str = Field(..., min_length=AIRPORT_CODE_LENGTH, max_length=AIRPORT_CODE_LENGTH)
    destination: str = Field(..., min_length=AIRPORT_CODE_LENGTH, max_length=AIRPORT_CODE_LENGTH)
    departure_time: datetime
    arrival_time: datetime
    price: float = Field(..., gt=MIN_CUSTOMER_SPENDING)
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
    city_code: str = Field(..., min_length=MIN_NIGHTS, max_length=MAX_NIGHTS)
    stars: int = Field(..., ge=1, le=5)
    rating: float = Field(..., ge=0, le=5)
    price_per_night: float = Field(..., gt=0)
    amenities: List[str]

class TripPackage(BaseModel):
    score: Optional[float] = None
    destination: str = Field(..., min_length=MIN_NIGHTS, max_length=MAX_NIGHTS)
    outbound_flight: Flight
    return_flight: Flight
    hotel: Hotel
    nights: int = Field(..., ge=HOTEL_STAY['MIN_NIGHTS'], le=HOTEL_STAY['MAX_NIGHTS'])

    @property
    def total_cost(self) -> float:
        return (self.outbound_flight.price + 
                self.return_flight.price + 
                self.hotel.price_per_night * self.nights)

    def calculate_score(self) -> float:
        return sum(score * weight for score, weight in zip(
            [self._calculate_price_score(),
             self._calculate_comfort_score(),
             self._calculate_convenience_score()],
            SCORING_WEIGHTS.values()
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