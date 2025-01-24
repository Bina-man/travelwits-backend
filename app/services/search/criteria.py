from dataclasses import dataclass
from typing import Optional
from ...config.config import MAX_SEARCH_RESULTS

@dataclass
class SearchCriteria:
    origin: str
    nights: int
    budget: float
    result_limit: int = MAX_SEARCH_RESULTS
    min_hotel_rating: Optional[float] = None
    max_stops: Optional[int] = None
