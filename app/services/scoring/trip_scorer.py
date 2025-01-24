from typing import Dict, List
from app.config.config import (
    AIRCRAFT_SCORES, 
    AIRLINE_SCORES, 
    FLIGHT_TIME_SCORES,
    FLIGHT_QUALITY_WEIGHTS,
    HOTEL_WEIGHTS, 
    MAX_HOTEL_SCORE, 
    STOP_PENALTY, 
    SCORING_WEIGHTS,
    HOTEL_AMENITY_SCORES
)
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
            'hotel': self._calculate_hotel_score(trip)
        }
        
        weighted_score = sum(
            score * getattr(self.weights, category)
            for category, score in scores.items()
        )
        
        total_flights = len(trip.outbound_path) + len(trip.return_path)
        complexity_factor = max(0.7, 1 - (total_flights - 2) * 0.1)
        
        final_score = weighted_score * complexity_factor
        return round(max(0, min(10, final_score / 10)), 2)

    def _calculate_price_score(self, trip: TripPackage, context: Dict) -> float:
        total_cost = trip.total_cost
        max_cost = context.get('budget', 8000)
        
        # Progressive scoring based on budget utilization
        cost_ratio = total_cost / max_cost
        if cost_ratio <= 0.3:
            return 100
        elif cost_ratio <= 0.5:
            return 90 - (cost_ratio - 0.3) * 100
        elif cost_ratio <= 0.7:
            return 70 - (cost_ratio - 0.5) * 100
        else:
            return max(30, 50 - (cost_ratio - 0.7) * 150)

    def _calculate_flight_score(self, trip: TripPackage) -> float:
        def score_flight_path(flights: List[Flight]) -> float:
            if not flights:
                return 0
                
            total_stops = sum(len(f.stops) for f in flights)
            num_segments = len(flights)
            
            # Calculate components with weights from FLIGHT_QUALITY_WEIGHTS
            time_score = self._calculate_time_score(flights)
            stops_score = 100 - (total_stops * STOP_PENALTY)
            airline_score = self._calculate_airline_score(flights)
            aircraft_score = self._calculate_aircraft_score(flights)
            
            # Apply quality weights
            weighted_score = (
                time_score * FLIGHT_QUALITY_WEIGHTS['TIME'] +
                stops_score * FLIGHT_QUALITY_WEIGHTS['STOPS'] +
                airline_score * FLIGHT_QUALITY_WEIGHTS['AIRLINE'] +
                aircraft_score * FLIGHT_QUALITY_WEIGHTS['AIRCRAFT']
            )
            
            # Apply segment penalty
            return max(0, weighted_score * (1 - (num_segments - 1) * 0.1))

        outbound_score = score_flight_path(trip.outbound_path)
        return_score = score_flight_path(trip.return_path)
        
        return (outbound_score * 0.6 + return_score * 0.4)

    def _calculate_time_score(self, flights: List[Flight]) -> float:
        scores = []
        for flight in flights:
            hour = flight.departure_time.hour
            score = None
            for time_range, (start, end, value) in FLIGHT_TIME_SCORES.items():
                if start <= hour <= end:
                    score = value
                    break
            scores.append(score or FLIGHT_TIME_SCORES['OFF_HOURS'][2])
        return sum(scores) / len(scores)

    def _calculate_airline_score(self, flights: List[Flight]) -> float:
        scores = []
        for flight in flights:
            if hasattr(flight, 'airline'):
                for tier in AIRLINE_SCORES.values():
                    if flight.airline in tier['airlines']:
                        scores.append(tier['score'])
                        break
                else:
                    scores.append(0)
        return sum(scores) / len(scores) if scores else 0

    def _calculate_aircraft_score(self, flights: List[Flight]) -> float:
        scores = []
        for flight in flights:
            if hasattr(flight, 'aircraft_type'):
                for category in AIRCRAFT_SCORES.values():
                    if flight.aircraft_type in category['types']:
                        scores.append(category['score'])
                        break
                else:
                    scores.append(0)
        return sum(scores) / len(scores) if scores else 0

    def _calculate_hotel_score(self, trip: TripPackage) -> float:
        if not hasattr(trip, 'hotel') or not trip.hotel:
            return 0
        
        # Base scores
        stars_score = min(40, trip.hotel.stars * HOTEL_WEIGHTS['STARS_MULTIPLIER'])
        rating_score = min(30, trip.hotel.rating * HOTEL_WEIGHTS['RATING_MULTIPLIER'])
        
        # Enhanced amenity scoring using HOTEL_AMENITY_SCORES
        amenity_score = 0
        for amenity in trip.hotel.amenities:
            for category in HOTEL_AMENITY_SCORES.values():
                if amenity.upper() in category:
                    amenity_score += category[amenity.upper()]
        amenity_score = min(30, amenity_score * HOTEL_WEIGHTS['AMENITY_MULTIPLIER'] / 100)
        
        total_score = stars_score + rating_score + amenity_score
        return min(MAX_HOTEL_SCORE, total_score)