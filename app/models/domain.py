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
    outbound_path: List[Flight] = Field(default_factory=list)
    return_path: List[Flight] = Field(default_factory=list)
    total_cost: float = 0
    hotel: Hotel
    nights: int = Field(..., ge=HOTEL_STAY['MIN_NIGHTS'], le=HOTEL_STAY['MAX_NIGHTS'])

    @property
    def outbound_flight(self) -> Flight:
        return self.outbound_path[0] if self.outbound_path else None
        
    @property
    def return_flight(self) -> Flight:
        return self.return_path[0] if self.return_path else None

    @property
    def total_cost(self) -> float:
        return (sum(f.price for f in self.outbound_path) + 
                sum(f.price for f in self.return_path) + 
                self.hotel.price_per_night * self.nights)

    def _calculate_convenience_score(self) -> float:
        total_stops = sum(len(f.stops) for f in self.outbound_path + self.return_path)
        score = 10.0 - total_stops * 2
        if 8 <= self.outbound_flight.departure_time.hour <= 20:
            score += 2
        return max(score, 0)