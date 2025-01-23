import json
from typing import List
from datetime import datetime
from ..models.flight import Flight
from ..models.hotel import Hotel
from ..config.settings import FLIGHTS_FILE, HOTELS_FILE

class DataLoader:
    async def load_flights(self) -> List[Flight]:
        """Load flights from JSON file."""
        with open(FLIGHTS_FILE, 'r') as f:
            flights_data = json.load(f)
            
        return [
            Flight(
                id=f["id"],
                origin=f["from"],
                destination=f["to"],
                departure_time=datetime.strptime(f["departure_time"], "%H:%M").time(),
                arrival_time=datetime.strptime(f["arrival_time"], "%H:%M").time(),
                price=f["price"],
                stops=f.get("stops", [])
            )
            for f in flights_data
        ]
        
    async def load_hotels(self) -> List[Hotel]:
        """Load hotels from JSON file."""
        with open(HOTELS_FILE, 'r') as f:
            hotels_data = json.load(f)
            
        return [
            Hotel(
                id=h["id"],
                name=h["name"],
                city_code=h["city_code"],
                stars=h["stars"],
                rating=h["rating"],
                price_per_night=h["price_per_night"],
                amenities=h["amenities"]
            )
            for h in hotels_data
        ] 