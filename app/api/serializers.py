from typing import Dict, Any, List
from ..models.domain import TripPackage, Flight, Hotel

class TravelSerializer:
    @staticmethod
    def format_trip_package(trip: TripPackage) -> dict:
        return {
            "destination": trip.destination,
            "outbound_flights": [TravelSerializer.format_flight(f) for f in trip.outbound_path],
            "return_flights": [TravelSerializer.format_flight(f) for f in trip.return_path],
            "hotel": TravelSerializer.format_hotel(trip.hotel),
            "total_cost": trip.total_cost,
            "score": trip.score,
            "nights": trip.nights
        }
    
    @staticmethod
    def format_flight(flight: Flight) -> Dict[str, Any]:
        return {
            "id": flight.id,
            "from": flight.origin,
            "to": flight.destination,
            "departure_time": flight.departure_time.strftime('%H:%M'),
            "arrival_time": flight.arrival_time.strftime('%H:%M'),
            "price": flight.price,
            "stops": flight.stops
        }
    
    @staticmethod
    def format_hotel(hotel: Hotel) -> Dict[str, Any]:
        return {
            "id": hotel.id,
            "name": hotel.name,
            "stars": hotel.stars,
            "rating": hotel.rating,
            "price_per_night": hotel.price_per_night,
            "amenities": hotel.amenities
        }

    @staticmethod
    def format_multi_city_trip(trip: List[Any]) -> Dict[str, Any]:
        return {
            "stays": [
                {
                    "city": stay.city,
                    "flight": TravelSerializer.format_flight(stay.arrival_flight),
                    "hotel": TravelSerializer.format_hotel(stay.hotel) if stay.hotel else None,
                    "nights": stay.nights
                } for stay in trip
            ],
            "total_cost": sum(stay.cost for stay in trip),
            "total_nights": sum(stay.nights for stay in trip),
            "cities_visited": [stay.city for stay in trip]
        }