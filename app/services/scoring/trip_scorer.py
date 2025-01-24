from typing import Dict
from app.config.config import FLIGHT_TIME_SCORES, HOTEL_WEIGHTS, MAX_HOTEL_SCORE, STOP_PENALTY, SCORING_WEIGHTS
from ...models.domain import Flight, TripPackage
from dataclasses import dataclass

@dataclass
class ScoreWeights:
    price: float = SCORING_WEIGHTS['PRICE']
    flight: float = SCORING_WEIGHTS['FLIGHT']
    hotel: float = SCORING_WEIGHTS['HOTEL']
    destination: float = SCORING_WEIGHTS['DESTINATION']

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
            
            for _, (start, end, score) in FLIGHT_TIME_SCORES.items():
                if start <= hour <= end:
                    time_score = score
                    break
            
            stops_penalty = len(flight.stops) * STOP_PENALTY
            return max(0, time_score - stops_penalty)

        return (score_flight(trip.outbound_flight) + 
                score_flight(trip.return_flight)) / 2

    def _calculate_hotel_score(self, trip: TripPackage) -> float:
        return min(MAX_HOTEL_SCORE, (
            (trip.hotel.stars * HOTEL_WEIGHTS['STARS_MULTIPLIER']) +
            (trip.hotel.rating * HOTEL_WEIGHTS['RATING_MULTIPLIER']) +
            (len(trip.hotel.amenities) * HOTEL_WEIGHTS['AMENITY_MULTIPLIER'])
        ))

    def _calculate_destination_score(self, trip: TripPackage, context: Dict) -> float:
        return context['destination_popularity'].get(trip.destination, 0) * 100
