# app/services/stats.py
from collections import Counter, defaultdict
from datetime import datetime
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class SearchStats:
    def __init__(self):
        self.total_searches = 0
        self.successful_searches = 0
        self.failed_searches = 0
        self.popular_origins = Counter()
        self.popular_destinations = Counter()
        self.search_times_by_route = defaultdict(list)
        self.average_budgets = defaultdict(list)
        self.unique_users: Set[str] = set()  # If you implement user tracking
        self.last_reset = datetime.now()

    def log_search(self, origin: str, destinations: List[str], budget: float, 
                  success: bool, duration_ms: float):
        """Log a single search attempt"""
        self.total_searches += 1
        if success:
            self.successful_searches += 1
        else:
            self.failed_searches += 1

        self.popular_origins[origin] += 1
        for dest in destinations:
            self.popular_destinations[dest] += 1
            route = f"{origin}-{dest}"
            self.search_times_by_route[route].append(duration_ms)
            self.average_budgets[route].append(budget)

    def get_stats_report(self) -> Dict:
        """Generate a comprehensive stats report"""
        total_duration = (datetime.now() - self.last_reset).total_seconds()
        
        # Calculate most popular routes
        route_stats = {}
        for route, times in self.search_times_by_route.items():
            avg_time = sum(times) / len(times)
            avg_budget = sum(self.average_budgets[route]) / len(self.average_budgets[route])
            success_rate = len([t for t in times if t > 0]) / len(times)
            
            route_stats[route] = {
                "searches": len(times),
                "avg_time_ms": round(avg_time, 2),
                "avg_budget": round(avg_budget, 2),
                "success_rate": round(success_rate * 100, 1)
            }

        return {
            "general": {
                "total_searches": self.total_searches,
                "successful_searches": self.successful_searches,
                "failed_searches": self.failed_searches,
                "success_rate": round((self.successful_searches / self.total_searches * 100 if self.total_searches > 0 else 0), 1),
                "unique_users": len(self.unique_users),
                "tracking_duration_hours": round(total_duration / 3600, 1)
            },
            "popular_origins": dict(self.popular_origins.most_common(5)),
            "popular_destinations": dict(self.popular_destinations.most_common(5)),
            "route_stats": dict(sorted(route_stats.items(), 
                                     key=lambda x: x[1]['searches'], 
                                     reverse=True)[:10])
        }

    def reset_stats(self):
        """Reset all statistics"""
        self.__init__()