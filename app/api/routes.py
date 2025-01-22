# api/routes.py
from ..models.multi_city import MultiCityFlight, MultiCitySearchEngine
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
import logging
import time  # Add this import for time.time()
from datetime import datetime 
from ..services.search import TravelSearchEngine
from ..models.domain import Flight, Hotel

router = APIRouter()
logger = logging.getLogger(__name__)

class TravelAPI:
    def __init__(self, flights: List[Dict], hotels: List[Dict]):
        # Initialize both search engines
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
        
        hotels = [
            Hotel(
                id=h['id'],
                name=h['name'],
                city_code=h['city_code'],
                stars=int(h['stars']),
                rating=float(h['rating']),
                price_per_night=float(h['price_per_night']),
                amenities=h['amenities']
            ) for h in raw_hotels
        ]
        
        return TravelSearchEngine(flights, hotels)
    
    def _initialize_multi_city_engine(self, raw_flights: List[Dict], raw_hotels: List[Dict]) -> MultiCitySearchEngine:
        # Convert raw flights to MultiCityFlight objects
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
        
        # Group hotels by city code
        hotels_by_city = {}
        for h in raw_hotels:
            city_code = h['city_code']
            if city_code not in hotels_by_city:
                hotels_by_city[city_code] = []
                
            hotel = Hotel(
                id=h['id'],
                name=h['name'],
                city_code=city_code,
                stars=int(h['stars']),
                rating=float(h['rating']),
                price_per_night=float(h['price_per_night']),
                amenities=h['amenities']
            )
            hotels_by_city[city_code].append(hotel)
        
        return MultiCitySearchEngine(flights, hotels_by_city)
    

@router.get("/search")
async def search_trips(
    origin: str = Query(..., min_length=3, max_length=3, description="Airport code (e.g., JFK)"),
    nights: int = Query(..., ge=1, le=30, description="Number of nights to stay"),
    budget: float = Query(..., ge=0, description="Maximum budget for the trip")
):
    start_time = time.time()
    try:
        logger.info(f"Searching trips for origin={origin}, nights={nights}, budget={budget}")
        
        if not hasattr(router, "travel_api"):
            logger.error("Travel API not initialized")
            raise HTTPException(status_code=503, detail="Service not initialized")

        # Add await here since search_trips is async
        trip_packages = await router.travel_api.search_engine.search_trips(
            origin=origin.upper(),
            nights=int(nights),
            budget=float(budget)
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        if not trip_packages:
            # Log failed search before raising exception
            router.stats.log_search(
                origin=origin,
                destinations=[],
                budget=budget,
                success=False,
                duration_ms=duration_ms
            )
            logger.warning(f"No trips found for origin={origin}, nights={nights}, budget={budget}")
            raise HTTPException(status_code=404, detail="No trips found within budget")
        
        results = [_format_trip_package(trip) for trip in trip_packages]
        
        # Log successful search
        router.stats.log_search(
            origin=origin,
            destinations=[trip.destination for trip in trip_packages],
            budget=budget,
            success=True,
            duration_ms=duration_ms
        )
        
        logger.info(f"Successfully returning {len(results)} trips")
        return results
        
    except HTTPException as he:
        raise he
    except ValueError as ve:
        duration_ms = (time.time() - start_time) * 1000
        router.stats.log_search(
            origin=origin,
            destinations=[],
            budget=budget,
            success=False,
            duration_ms=duration_ms
        )
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=422, detail=f"Invalid parameter value: {str(ve)}")
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        router.stats.log_search(
            origin=origin,
            destinations=[],
            budget=budget,
            success=False,
            duration_ms=duration_ms
        )
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
@router.get("/stats")
async def get_search_statistics():
    """Get search statistics"""
    try:
        if not hasattr(router, "stats"):
            raise HTTPException(status_code=503, detail="Statistics not initialized")
        
        report = router.stats.get_stats_report()
        logger.info("Successfully retrieved search statistics")
        return report
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")

def _format_trip_package(trip):
    return {
        "destination": trip.destination,
        "outbound_flight": _format_flight(trip.outbound_flight),
        "return_flight": _format_flight(trip.return_flight),
        "hotel": _format_hotel(trip.hotel),
        "total_cost": trip.total_cost,
        "score": trip.calculate_score(),
        "nights": trip.nights
    }

def _format_flight(flight):
    return {
        "id": flight.id,
        "from": flight.origin,
        "to": flight.destination,
        "departure_time": flight.departure_time.strftime('%H:%M'),
        "arrival_time": flight.arrival_time.strftime('%H:%M'),
        "price": flight.price,
        "stops": flight.stops
    }

def _format_hotel(hotel):
    return {
        "id": hotel.id,
        "name": hotel.name,
        "stars": hotel.stars,
        "rating": hotel.rating,
        "price_per_night": hotel.price_per_night,
        "amenities": hotel.amenities
    }


@router.get("/multi-city-search")
async def search_multi_city_trips(
    origin: str = Query(..., min_length=3, max_length=3),
    must_visit: str = Query(..., description="Comma-separated list of required city codes"),
    optional_visit: str = Query("", description="Comma-separated list of optional city codes"),
    total_nights: int = Query(..., ge=1, le=30),
    budget: float = Query(..., gt=0)
):
    try:
        must_visit_cities = [city.strip().upper() for city in must_visit.split(',')]
        optional_cities = [city.strip().upper() for city in optional_visit.split(',') if city]

        logger.info(f"Searching multi-city trips for origin={origin}, "
                   f"must_visit={must_visit_cities}, optional={optional_cities}, "
                   f"nights={total_nights}, budget={budget}")

        # Fix: Changed travel_api to router.travel_api
        if not hasattr(router, "travel_api"):
            logger.error("Travel API not initialized")
            raise HTTPException(status_code=503, detail="Service not initialized")

        # Fix: Changed travel_api to router.travel_api
        trips = router.travel_api.multi_city_engine.search_multi_city_trips(
            origin=origin.upper(),
            must_visit_cities=must_visit_cities,
            optional_cities=optional_cities,
            total_nights=total_nights,
            budget=budget
        )

        if not trips:
            raise HTTPException(status_code=404, detail="No valid multi-city trips found")

        # Format results
        results = []
        for trip in trips:
            formatted_trip = {
                "stays": [
                    {
                        "city": stay.city,
                        "flight": {
                            "id": stay.arrival_flight.id,
                            "from": stay.arrival_flight.origin,
                            "to": stay.arrival_flight.destination,
                            "departure_time": stay.arrival_flight.departure_time.strftime('%H:%M'),
                            "arrival_time": stay.arrival_flight.arrival_time.strftime('%H:%M'),
                            "price": stay.arrival_flight.price,
                            "stops": stay.arrival_flight.stops
                        },
                        "hotel": {
                            "id": stay.hotel.id,
                            "name": stay.hotel.name,
                            "stars": stay.hotel.stars,
                            "rating": stay.hotel.rating,
                            "price_per_night": stay.hotel.price_per_night,
                            "amenities": stay.hotel.amenities
                        } if stay.hotel else None,
                        "nights": stay.nights
                    } for stay in trip
                ],
                "total_cost": sum(stay.cost for stay in trip),
                "total_nights": sum(stay.nights for stay in trip),
                "cities_visited": [stay.city for stay in trip]
            }
            results.append(formatted_trip)

        return results

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )
