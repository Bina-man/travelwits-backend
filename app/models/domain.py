from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum

class TravelClass(Enum):
    """
    Enumeration of available travel classes.
    
    Attributes:
        ECONOMY: Standard economy class
        BUSINESS: Business class service
        FIRST: First class service
    """
    ECONOMY = "economy"
    BUSINESS = "business"
    FIRST = "first"

@dataclass
class Airport:
    """
    Represents an airport with its basic information.
    
    Attributes:
        code (str): IATA airport code (e.g., 'JFK', 'LAX')
        city (str): City where the airport is located
        timezone (str): Timezone identifier for the airport location
    """
    code: str
    city: str
    timezone: str

@dataclass
class Flight:
    """
    Represents a flight with its details and routing information.
    
    Attributes:
        id (str): Unique identifier for the flight
        origin (str): Origin airport code
        destination (str): Destination airport code
        departure_time (datetime): Scheduled departure time
        arrival_time (datetime): Scheduled arrival time
        price (float): Flight price
        stops (List[str]): List of stopover airport codes
    """
    id: str
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price: float
    stops: List[str]
    
    @property
    def duration(self) -> timedelta:
        """
        Calculate the flight duration.
        
        Returns:
            timedelta: Total flight duration
        """
        return self.arrival_time - self.departure_time
    
    @property
    def is_direct(self) -> bool:
        """
        Check if the flight is direct (no stops).
        
        Returns:
            bool: True if direct flight, False otherwise
        """
        return len(self.stops) == 0

@dataclass
class Hotel:
    """
    Represents a hotel with its details and amenities.
    
    Attributes:
        id (str): Unique identifier for the hotel
        name (str): Hotel name
        city_code (str): City code where hotel is located
        stars (int): Hotel star rating (1-5)
        rating (float): Guest rating (0.0-5.0)
        price_per_night (float): Price per night
        amenities (List[str]): Available amenities
    """
    id: str
    name: str
    city_code: str
    stars: int
    rating: float
    price_per_night: float
    amenities: List[str]

@dataclass
class TripPackage:
    """
    Represents a complete trip package including flights and hotel.
    
    Attributes:
        destination (str): Destination city code
        outbound_flight (Flight): Outbound flight details
        return_flight (Flight): Return flight details
        hotel (Hotel): Hotel details
        nights (int): Number of nights stay
    """
    destination: str
    outbound_flight: Flight
    return_flight: Flight
    hotel: Hotel
    nights: int
    
    @property
    def total_cost(self) -> float:
        """
        Calculate the total cost of the trip package.
        
        Returns:
            float: Total cost including flights and hotel
        """
        return (self.outbound_flight.price + 
                self.return_flight.price + 
                self.hotel.price_per_night * self.nights)
    
    def calculate_score(self) -> float:
        """
        Calculate a comprehensive score for the trip package.
        
        Considers multiple factors including price, comfort, and convenience.
        
        Returns:
            float: Overall package score
        """
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
        """
        Calculate price-based score component.
        
        Returns:
            float: Price score
        """
        return 1000 / (self.total_cost / self.nights)

    def _calculate_comfort_score(self) -> float:
        """
        Calculate comfort-based score component.
        
        Considers hotel rating, stars, and amenities.
        
        Returns:
            float: Comfort score
        """
        return self.hotel.rating * self.hotel.stars + len(self.hotel.amenities) * 0.5

    def _calculate_convenience_score(self) -> float:
        """
        Calculate convenience-based score component.
        
        Considers flight stops and departure times.
        
        Returns:
            float: Convenience score
        """
        score = 10.0 - len(self.outbound_flight.stops) * 2 - len(self.return_flight.stops) * 2
        if 8 <= self.outbound_flight.departure_time.hour <= 20:
            score += 2
        return max(score, 0)