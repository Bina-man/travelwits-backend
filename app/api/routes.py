from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
from pydantic import BaseModel

from .serializers import TravelSerializer
from ..services.travel_api import TravelAPI # API definition for travel service. 
from ..config.config import MIN_NIGHTS, MAX_NIGHTS, AIRPORT_CODE_LENGTH

router = APIRouter()
logger = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    origin: str
    nights: int
    budget: float

class MultiCitySearchRequest(BaseModel):
    origin: str
    must_visit: List[str]
    optional_visit: Optional[List[str]] = None
    total_nights: int
    budget: float

@router.get("/search")
async def search_trips(
    origin: str = Query(..., min_length=AIRPORT_CODE_LENGTH, max_length=AIRPORT_CODE_LENGTH),
    nights: int = Query(..., ge=MIN_NIGHTS, le=MAX_NIGHTS),
    budget: float = Query(..., ge=0)
):
    try:
        logger.info(f"Searching trips for origin={origin}, nights={nights}, budget={budget}")
        
        if not hasattr(router, "travel_api"):
            raise HTTPException(status_code=503, detail="Service not initialized")

        return await router.travel_api.search_engine.search_trips(
            origin=origin.upper(),
            nights=nights,
            budget=budget
        )

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/multi-city-search")
async def search_multi_city_trips(request: MultiCitySearchRequest):
    try:
        logger.info(f"Multi-city search: {request}")
        
        if not hasattr(router, "travel_api"):
            raise HTTPException(status_code=503, detail="Service not initialized")

        trips = router.travel_api.multi_city_engine.search_multi_city_trips(
            origin=request.origin.upper(),
            must_visit_cities=request.must_visit,
            optional_cities=request.optional_visit or [],
            total_nights=request.total_nights,
            budget=request.budget
        )

        if not trips:
            raise HTTPException(status_code=404, detail="No valid multi-city trips found")

        return [TravelSerializer.format_multi_city_trip(trip) for trip in trips]

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))