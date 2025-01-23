from typing import Dict
from ...models.domain import Flight, TripPackage
from dataclasses import dataclass

@dataclass
class ScoreWeights:
    price: float = 0.35
    flight: float = 0.40
    hotel: float = 0.20
    destination: float = 0.05

class TripScorer:
    def __init__(self, weights: ScoreWeights = ScoreWeights()):
        self.weights = weights

    def calculate_score(self, trip: TripPackage, context: Dict) -> float:
        scores = {
            'price': self._calculate_price_score(trip, context),
            'flight': self._calculate_flight_score(trip),
            'hotel': self._calculate_hotel_score(trip),
            'destination': self._calculate_destination_score(trip, context)
        }
        
        weighted_score = sum(
            score * getattr(self.weights, category)
            for category, score in scores.items()
        )
        
        return round(max(0, min(100, weighted_score * 1.2)), 2)

    def _calculate_price_score(self, trip: TripPackage, context: Dict) -> float:
        total_cost = (
            trip.outbound_flight.price + 
            trip.return_flight.price + 
            trip.hotel.price_per_night * trip.nights
        )
        max_cost = (
            context['max_flight_price'] * 2 + 
            context['max_hotel_price'] * trip.nights
        )
        return max(0, 100 * (1 - (total_cost / max_cost))) * 1.5

    def _calculate_flight_score(self, trip: TripPackage) -> float:
        def score_flight(flight: Flight) -> float:
            hour = flight.departure_time.hour
            
            if 8 <= hour <= 11:
                time_score = 100
            elif 11 < hour <= 16:
                time_score = 80
            elif 6 <= hour < 8:
                time_score = 60
            elif 16 < hour <= 21:
                time_score = 50
            else:
                time_score = 20
            
            stops_penalty = len(flight.stops) * 40
            return max(0, time_score - stops_penalty)

        return (score_flight(trip.outbound_flight) + 
                score_flight(trip.return_flight)) / 2

    def _calculate_hotel_score(self, trip: TripPackage) -> float:
        return min(100, (
            (trip.hotel.stars * 18) +
            (trip.hotel.rating * 10) +
            (len(trip.hotel.amenities) * 7)
        ))

    def _calculate_destination_score(self, trip: TripPackage, context: Dict) -> float:
        return context['destination_popularity'].get(trip.destination, 0) * 100
