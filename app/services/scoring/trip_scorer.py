from typing import Dict, List
from app.config.config import (
    AIRCRAFT_SCORES, 
    AIRLINE_SCORES, 
    FLIGHT_QUALITY_WEIGHTS, 
    FLIGHT_TIME_SCORES, 
    HOTEL_WEIGHTS, 
    MAX_HOTEL_SCORE, 
    STOP_PENALTY, 
    SCORING_WEIGHTS
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
            'hotel': self._calculate_hotel_score(trip),
            'destination': self._calculate_destination_score(trip, context)
        }
        
        weighted_score = sum(
            score * getattr(self.weights, category)
            for category, score in scores.items()
        )
        
        return round(max(0, min(100, weighted_score * 1.5)), 2)/10

    def _calculate_price_score(self, trip: TripPackage, context: Dict) -> float:
        total_flight_cost = sum(f.price for f in trip.outbound_path + trip.return_path)
        total_cost = total_flight_cost + trip.hotel.price_per_night * trip.nights
        max_cost = context['max_flight_price'] * 2 + context['max_hotel_price'] * trip.nights
        return max(0, 100 * (1 - (total_cost / max_cost))) * 1.5

    def _calculate_flight_score(self, trip: TripPackage) -> float:
        def score_flight(flights: List[Flight]) -> float:
            total_score = 0
            for flight in flights:
                hour = flight.departure_time.hour
                
                # Time score
                time_score = FLIGHT_TIME_SCORES['OFF_HOURS'][2]  # Default
                for period, (start, end, score) in FLIGHT_TIME_SCORES.items():
                    if start <= hour <= end:
                        time_score = score
                        break
                        
                stops_penalty = len(flight.stops) * STOP_PENALTY
                
                # Airline score
                airline_score = 0
                if hasattr(flight, 'airline'):
                    for tier in AIRLINE_SCORES.values():
                        if flight.airline in tier['airlines']:
                            airline_score = tier['score']
                            break
                            
                # Aircraft score
                aircraft_score = 0
                if hasattr(flight, 'aircraft_type'):
                    for category in AIRCRAFT_SCORES.values():
                        if flight.aircraft_type in category['types']:
                            aircraft_score = category['score']
                            break
                
                total_score += (time_score + max(0, 100 - stops_penalty) + airline_score + aircraft_score) / len(flights)
            
            return total_score / 2

        return (score_flight(trip.outbound_path) + score_flight(trip.return_path)) / 2
    
    # def _calculate_flight_score(self, trip: TripPackage) -> float:
    #     def score_flight(flight: Flight) -> float:
    #         hour = flight.departure_time.hour
    #         time_score = FLIGHT_TIME_SCORES['OFF_HOURS'][2]
    #         for _, (start, end, score) in FLIGHT_TIME_SCORES.items():
    #             if start <= hour <= end:
    #                 time_score = score
    #                 break
            
    #         stops_penalty = len(flight.stops) * STOP_PENALTY
            
    #         # Airline scoring (20% if available)
    #         airline_score = 0
    #         if hasattr(flight, 'airline'):
    #             for tier in AIRLINE_SCORES.values():
    #                 if flight.airline in tier['airlines']:
    #                     airline_score = tier['score']
    #                     break
            
    #         # Aircraft scoring (10% if available)
    #         aircraft_score = 0
    #         if hasattr(flight, 'aircraft_type'):
    #             for category in AIRCRAFT_SCORES.values():
    #                 if flight.aircraft_type in category['types']:
    #                     aircraft_score = category['score']
    #                     break
            
    #         # Calculate weighted components
    #         weights = FLIGHT_QUALITY_WEIGHTS
    #         final_score = (
    #             time_score * weights['TIME'] +
    #             max(0, 100 - stops_penalty) * weights['STOPS'] +
    #             (airline_score * weights['AIRLINE'] if hasattr(flight, 'airline') else 0) +
    #             (aircraft_score * weights['AIRCRAFT'] if hasattr(flight, 'aircraft_type') else 0)
    #         )
            
    #         # Redistribute weights if airline/aircraft not available
    #         if not hasattr(flight, 'airline') and not hasattr(flight, 'aircraft_type'):
    #             final_score = final_score / (weights['TIME'] + weights['STOPS']) * 100
    #         elif not hasattr(flight, 'airline'):
    #             final_score = final_score / (1 - weights['AIRLINE']) * 100
    #         elif not hasattr(flight, 'aircraft_type'):
    #             final_score = final_score / (1 - weights['AIRCRAFT']) * 100
                
    #         return max(0, min(100, final_score))

    #     return (score_flight(trip.outbound_flight) + 
    #             score_flight(trip.return_flight)) / 2

    def _calculate_hotel_score(self, trip: TripPackage) -> float:
        return min(MAX_HOTEL_SCORE, (
            (trip.hotel.stars * HOTEL_WEIGHTS['STARS_MULTIPLIER']) +
            (trip.hotel.rating * HOTEL_WEIGHTS['RATING_MULTIPLIER']) +
            (len(trip.hotel.amenities) * HOTEL_WEIGHTS['AMENITY_MULTIPLIER'])
        ))

    def _calculate_destination_score(self, trip: TripPackage, context: Dict) -> float:
        return context['destination_popularity'].get(trip.destination, 0) * 100