from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchCriteria:
    origin: str
    nights: int
    budget: float
    result_limit: int = 10
    min_hotel_rating: Optional[float] = None
    max_stops: Optional[int] = None
