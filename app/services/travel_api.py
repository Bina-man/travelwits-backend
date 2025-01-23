from typing import List, Dict
from datetime import datetime
import logging
from .search.engine import TravelSearchEngine
from ..models.multi_city import MultiCityFlight, MultiCitySearchEngine
from ..models.domain import Flight, Hotel

logger = logging.getLogger(__name__)

class TravelAPI:
    def __init__(self, flights: List[Dict], hotels: List[Dict]):
        self.search_engine = self._initialize_engine(flights, hotels)
        self.multi_city_engine = self._initialize_multi_city_engine(flights, hotels)
    
    def _initialize_engine(self, raw_flights: List[Dict], raw_hotels: List[Dict]) -> TravelSearchEngine:
        flights = [
            Flight(
                id=f['id'],
                origin=f['from'],
                destination=f['to'],
                departure_time=datetime.strptime(f['departure_time'], '%H:%M'),
                arrival_time=datetime.strptime(f['arrival_time'], '%H:%M'),
                price=float(f['price']),
                stops=f.get('stops', [])
            ) for f in raw_flights
        ]
        
        hotels = []
        for h in raw_hotels:
            try:
                hotel = Hotel(
                    id=h['id'],
                    name=h['name'],
                    city_code=h['city_code'],
                    stars=int(h['stars']),
                    rating=min(float(h['rating']), 5.0),
                    price_per_night=float(h['price_per_night']),
                    amenities=h['amenities']
                )
                hotels.append(hotel)
            except ValueError as e:
                logger.warning(f"Skipping invalid hotel {h['id']}: {str(e)}")
                continue
        
        return TravelSearchEngine(flights, hotels)

    def _initialize_multi_city_engine(self, raw_flights: List[Dict], raw_hotels: List[Dict]) -> MultiCitySearchEngine:
        flights = [
            MultiCityFlight(
                id=f['id'],
                origin=f['from'],
                destination=f['to'],
                departure_time=datetime.strptime(f['departure_time'], '%H:%M'),
                arrival_time=datetime.strptime(f['arrival_time'], '%H:%M'),
                price=float(f['price']),
                stops=f.get('stops', [])
            ) for f in raw_flights
        ]
        
        hotels_by_city = {}
        for h in raw_hotels:
            try:
                city_code = h['city_code']
                if city_code not in hotels_by_city:
                    hotels_by_city[city_code] = []
                
                hotel = Hotel(
                    id=h['id'],
                    name=h['name'],
                    city_code=city_code,
                    stars=int(h['stars']),
                    rating=min(float(h['rating']), 5.0),
                    price_per_night=float(h['price_per_night']),
                    amenities=h['amenities']
                )
                hotels_by_city[city_code].append(hotel)
            except ValueError as e:
                logger.warning(f"Skipping invalid hotel {h['id']}: {str(e)}")
                continue
        
        return MultiCitySearchEngine(flights, hotels_by_city)