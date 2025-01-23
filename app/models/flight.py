from pydantic import BaseModel
from typing import List
from datetime import time

class Flight(BaseModel):
    id: str
    origin: str
    destination: str
    departure_time: time
    arrival_time: time
    price: float
    stops: List[str] = [] 