from typing import List
from ...models.domain import Flight, Hotel
from .index_manager import TravelIndexManager
from .trip_search import TripSearch
from ..scoring.trip_scorer import TripScorer
from ..cache import TravelCache


class TravelSearchEngine:
    def __init__(self, flights: List[Flight], hotels: List[Hotel]):
        self.index_manager = TravelIndexManager(flights, hotels)
        self.scorer = TripScorer()
        self.cache = TravelCache()
        self.search_engine = TripSearch(
            self.index_manager,
            self.scorer,
            self.cache
        )

    async def search_trips(self, **kwargs):
        from .criteria import SearchCriteria
        criteria = SearchCriteria(**kwargs)
        return await self.search_engine.search(criteria)

    def invalidate_cache(self):
        self.cache.invalidate_pattern("search_trips:*")