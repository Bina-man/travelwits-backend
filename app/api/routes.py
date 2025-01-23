# api/routes.py
from ..models.multi_city import MultiCityFlight, MultiCitySearchEngine
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict
import logging
import time
from datetime import datetime 
from ..services.search import TravelSearchEngine
from ..models.domain import Flight, Hotel

router = APIRouter()
logger = logging.getLogger(__name__)

class TravelAPI:
    """
    Main API handler for travel-related operations.
    
    Manages initialization of search engines and provides interface
    for both single-destination and multi-city travel searches.
    
    Attributes:
        search_engine (TravelSearchEngine): Engine for single-destination searches
        multi_city_engine (MultiCitySearchEngine): Engine for multi-city searches
    """

    def __init__(self, flights: List[Dict], hotels: List[Dict]):
        """
        Initialize both search engines with flight and hotel data.
        
        Args:
            flights: List of raw flight dictionaries
            hotels: List of raw hotel dictionaries
        """
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
        "score": getattr(trip, 'score', trip.calculate_score()),
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
    """
    Search for multi-city trip packages.
    
    Args:
        origin: Starting airport code (3 letters)
        must_visit: Comma-separated list of required city codes
        optional_visit: Comma-separated list of optional city codes
        total_nights: Total number of nights for the trip (1-30)
        budget: Maximum total budget
        
    Returns:
        List of matching multi-city trip packages
        
    Raises:
        HTTPException: If service is not initialized or no results found
    """
    try:
        must_visit_cities = [city.strip().upper() for city in must_visit.split(',')]
        optional_cities = [city.strip().upper() for city in optional_visit.split(',') if city]

        logger.info(f"Searching multi-city trips for origin={origin}, "
                   f"must_visit={must_visit_cities}, optional={optional_cities}, "
                   f"nights={total_nights}, budget={budget}")

        if not hasattr(router, "travel_api"):
            logger.error("Travel API not initialized")
            raise HTTPException(status_code=503, detail="Service not initialized")

        trips = router.travel_api.multi_city_engine.search_multi_city_trips(
            origin=origin.upper(),
            must_visit_cities=must_visit_cities,
            optional_cities=optional_cities,
            total_nights=total_nights,
            budget=budget
        )

        if not trips:
            raise HTTPException(status_code=404, detail="No valid multi-city trips found")

        return [format_multi_city_trip(trip) for trip in trips]

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

def format_multi_city_trip(trip):
    """
    Format a multi-city trip for API response.
    
    Args:
        trip: Raw multi-city trip data
        
    Returns:
        Dict: Formatted trip data for API response
    """
    return {
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
