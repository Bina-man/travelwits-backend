from pydantic import BaseModel
from typing import List

class Hotel(BaseModel):
    id: str
    name: str
    city_code: str
    stars: int
    rating: float
    price_per_night: float
    amenities: List[str]