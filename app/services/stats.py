# app/services/stats.py
from collections import Counter, defaultdict
from datetime import datetime
import logging
from typing import Dict, List, Set, Optional, Union

logger = logging.getLogger(__name__)

class SearchStats:
    """
    Tracks and analyzes search statistics for the travel search system.
    
    This class maintains various metrics and analytics about search operations,
    including success rates, popular routes, timing statistics, and budget analysis.
    It provides functionality to log individual searches and generate comprehensive
    reports about system usage and performance.
    
    Attributes:
        total_searches (int): Total number of searches performed
        successful_searches (int): Number of searches that found results
        failed_searches (int): Number of searches that found no results
        popular_origins (Counter): Counter tracking popular origin locations
        popular_destinations (Counter): Counter tracking popular destinations
        search_times_by_route (defaultdict): Dictionary tracking search durations by route
        average_budgets (defaultdict): Dictionary tracking budget statistics by route
        unique_users (Set[str]): Set of unique user identifiers
        last_reset (datetime): Timestamp of the last statistics reset
    """

    def __init__(self):
        """
        Initialize search statistics tracking with zero values and empty collections.
        Sets up all necessary counters and data structures for tracking search metrics.
        """
        self.total_searches = 0
        self.successful_searches = 0
        self.failed_searches = 0
        self.popular_origins = Counter()
        self.popular_destinations = Counter()
        self.search_times_by_route = defaultdict(list)
        self.average_budgets = defaultdict(list)
        self.unique_users: Set[str] = set()
        self.last_reset = datetime.now()

    def log_search(self, 
                  origin: str, 
                  destinations: List[str], 
                  budget: float, 
                  success: bool, 
                  duration_ms: float,
                  user_id: Optional[str] = None) -> None:
        """
        Log a single search attempt with its results and metrics.

        Records various aspects of a search operation including origin, destinations,
        budget, success status, and performance metrics. Updates all relevant
        counters and statistics.

        Args:
            origin: Origin airport/city code
            destinations: List of destination airport/city codes searched
            budget: Search budget amount specified by user
            success: Whether the search found valid results
            duration_ms: Search operation duration in milliseconds
            user_id: Optional unique identifier for the user performing the search

        Example:
            >>> stats.log_search(
            ...     origin="NYC",
            ...     destinations=["LAX", "SFO"],
            ...     budget=1000.0,
            ...     success=True,
            ...     duration_ms=150.5,
            ...     user_id="user123"
            ... )
        """
        # Update basic counters
        self.total_searches += 1
        if success:
            self.successful_searches += 1
        else:
            self.failed_searches += 1

        # Track user if provided
        if user_id:
            self.unique_users.add(user_id)

        # Update origin and destination statistics
        self.popular_origins[origin] += 1
        for dest in destinations:
            self.popular_destinations[dest] += 1
            route = f"{origin}-{dest}"
            self.search_times_by_route[route].append(duration_ms)
            self.average_budgets[route].append(budget)

    def get_stats_report(self) -> Dict[str, Union[Dict, List]]:
        """
        Generate a comprehensive statistics report.

        Compiles various statistics into a structured report including general metrics,
        popular routes, performance statistics, and budget analysis.

        Returns:
            Dictionary containing:
                - general: Overall statistics (total searches, success rates, etc.)
                - popular_origins: Top 5 most searched origin locations
                - popular_destinations: Top 5 most searched destinations
                - route_stats: Detailed statistics for top 10 routes including:
                    - searches: Number of searches for the route
                    - avg_time_ms: Average search time in milliseconds
                    - avg_budget: Average budget specified for the route
                    - success_rate: Percentage of successful searches

        Example:
            >>> stats.get_stats_report()
            {
                'general': {
                    'total_searches': 100,
                    'success_rate': 85.5,
                    ...
                },
                'popular_origins': {'NYC': 50, 'LAX': 30, ...},
                ...
            }
        """
        total_duration = (datetime.now() - self.last_reset).total_seconds()
        
        # Calculate route-specific statistics
        route_stats = self._calculate_route_stats()

        return {
            "general": {
                "total_searches": self.total_searches,
                "successful_searches": self.successful_searches,
                "failed_searches": self.failed_searches,
                "success_rate": self._calculate_success_rate(),
                "unique_users": len(self.unique_users),
                "tracking_duration_hours": round(total_duration / 3600, 1)
            },
            "popular_origins": dict(self.popular_origins.most_common(5)),
            "popular_destinations": dict(self.popular_destinations.most_common(5)),
            "route_stats": dict(sorted(route_stats.items(), 
                                     key=lambda x: x[1]['searches'], 
                                     reverse=True)[:10])
        }

    def _calculate_route_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Calculate detailed statistics for each route.

        Returns:
            Dictionary mapping routes to their statistics including search count,
            average time, average budget, and success rate.
        """
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
        return route_stats

    def _calculate_success_rate(self) -> float:
        """
        Calculate the overall success rate of searches.

        Returns:
            float: Percentage of successful searches, rounded to 1 decimal place.
        """
        if self.total_searches == 0:
            return 0.0
        return round((self.successful_searches / self.total_searches * 100), 1)

    def reset_stats(self) -> None:
        """
        Reset all statistics counters and metrics to their initial state.
        This includes clearing all counters, lists, and setting the reset timestamp.
        """
        self.__init__()