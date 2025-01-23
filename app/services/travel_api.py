from typing import List, Dict, Optional
from .search import SearchEngine
from .cache import TravelCache
from .data_loader import DataLoader

class TravelAPI:
    def __init__(self):
        self.data_loader = DataLoader()
        self.cache = TravelCache()
        self.search_engine = SearchEngine(self.cache)
        
    async def initialize(self):
        """Initialize the API with data."""
        flights = await self.data_loader.load_flights()
        hotels = await self.data_loader.load_hotels()
        self.search_engine.build_indexes(flights, hotels)
        
    async def search_trips(
        self,
        origin: str,
        destination: Optional[str],
        nights: int,
        budget: float
    ) -> List[Dict]:
        """Search for trip packages."""
        if destination:
            return await self.search_engine.search_trips(
                origin=origin,
                destination=destination,
                nights=nights,
                budget=budget
            )
        else:
            return await self.search_engine.search_all_destinations(
                origin=origin,
                nights=nights,
                budget=budget
            ) 