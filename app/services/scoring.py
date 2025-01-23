from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from dataclasses import dataclass
from enum import Enum

class ScoreFactors(Enum):
    """
    Enumeration of factors used in search result scoring.
    
    Attributes:
        PRICE: Price-related scoring factor
        POPULARITY: Destination popularity factor
        SEASONALITY: Seasonal timing factor
        HISTORICAL_DEMAND: Historical booking demand factor
        AVAILABILITY: Current availability factor
    """
    PRICE = "price"
    POPULARITY = "popularity"
    SEASONALITY = "seasonality"
    HISTORICAL_DEMAND = "historical_demand"
    AVAILABILITY = "availability"

@dataclass
class SearchResultScore:
    """
    Data class to hold scoring results for a search result.
    
    Attributes:
        raw_score (float): Unweighted average of all factor scores
        weighted_score (float): Final score after applying factor weights
        factor_scores (Dict[ScoreFactors, float]): Individual scores for each factor
    """
    raw_score: float
    weighted_score: float
    factor_scores: Dict[ScoreFactors, float]

class SearchScorer:
    """
    Handles the scoring of search results based on multiple factors.
    
    This class implements a comprehensive scoring system that considers
    multiple factors including price, popularity, seasonality, and more.
    """
    
    def __init__(self):
        """
        Initialize the SearchScorer with default weight configuration
        and seasonality data.
        """
        self.weight_config = {
            ScoreFactors.PRICE: 0.35,
            ScoreFactors.POPULARITY: 0.25,
            ScoreFactors.SEASONALITY: 0.15,
            ScoreFactors.HISTORICAL_DEMAND: 0.15,
            ScoreFactors.AVAILABILITY: 0.10
        }
        
        self.seasonality_data = self._initialize_seasonality_data()
        
    def _initialize_seasonality_data(self) -> Dict[str, Dict[int, float]]:
        """
        Initialize seasonality scores for destinations by month.
        
        Returns:
            Dict[str, Dict[int, float]]: Mapping of destination types to their
            monthly seasonality scores (1-12).
        """
        return {
            "default": {month: 1.0 for month in range(1, 13)},
            "beach": {
                1: 0.6, 2: 0.6, 3: 0.7, 4: 0.8, 5: 0.9,
                6: 1.0, 7: 1.0, 8: 1.0, 9: 0.9, 10: 0.8,
                11: 0.7, 12: 0.6
            },
            "ski": {
                1: 1.0, 2: 1.0, 3: 0.9, 4: 0.7, 5: 0.5,
                6: 0.4, 7: 0.4, 8: 0.4, 9: 0.5, 10: 0.7,
                11: 0.9, 12: 1.0
            }
        }

    def _normalize_score(self, value: float, min_val: float, max_val: float) -> float:
        """
        Normalize a score between 0 and 1.
        
        Args:
            value: Raw value to normalize
            min_val: Minimum possible value
            max_val: Maximum possible value
            
        Returns:
            float: Normalized score between 0 and 1
        """
        if max_val == min_val:
            return 1.0
        return (value - min_val) / (max_val - min_val)

    def _calculate_price_score(self, price: float, avg_price: float, std_price: float) -> float:
        """
        Calculate price score using a normal distribution.
        
        Args:
            price: Price to score
            avg_price: Average price in the dataset
            std_price: Standard deviation of prices
            
        Returns:
            float: Price score between 0 and 1
        """
        if price <= 0 or avg_price <= 0:
            return 0.0
        
        # Lower prices should get higher scores
        z_score = (avg_price - price) / (std_price if std_price > 0 else avg_price * 0.1)
        score = 1 / (1 + np.exp(-z_score))  # Sigmoid function
        return min(max(score, 0.0), 1.0)

    def _calculate_seasonality_score(self, destination: str, date: datetime) -> float:
        """
        Calculate seasonality score based on destination and time of year.
        
        Args:
            destination: Destination code or name
            date: Travel date
            
        Returns:
            float: Seasonality score between 0 and 1
        """
        destination_type = "default"  # This could be determined by destination characteristics
        month = date.month
        return self.seasonality_data.get(destination_type, self.seasonality_data["default"])[month]

    def score_search_result(self, result: Dict[str, Any], context: Dict[str, Any]) -> SearchResultScore:
        """
        Score a single search result based on multiple factors.
        
        Args:
            result: Search result to score
            context: Contextual data for scoring (averages, statistics, etc.)
            
        Returns:
            SearchResultScore: Comprehensive scoring result
        """
        factor_scores = {}
        
        # Price scoring
        price = float(result.get("price", 0))
        avg_price = float(context.get("avg_price", price))
        std_price = float(context.get("std_price", avg_price * 0.1))
        factor_scores[ScoreFactors.PRICE] = self._calculate_price_score(price, avg_price, std_price)
        
        # Popularity scoring
        popularity = result.get("popularity", 0)
        max_popularity = context.get("max_popularity", 100)
        factor_scores[ScoreFactors.POPULARITY] = self._normalize_score(
            popularity, 0, max_popularity
        )
        
        # Seasonality scoring
        date = datetime.strptime(result.get("date", context.get("search_date")), "%Y-%m-%d")
        factor_scores[ScoreFactors.SEASONALITY] = self._calculate_seasonality_score(
            result.get("destination"), date
        )
        
        # Historical demand scoring
        historical_demand = result.get("historical_demand", 50)
        factor_scores[ScoreFactors.HISTORICAL_DEMAND] = self._normalize_score(
            historical_demand, 0, 100
        )
        
        # Availability scoring
        availability = result.get("availability", 50)
        factor_scores[ScoreFactors.AVAILABILITY] = self._normalize_score(
            availability, 0, 100
        )
        
        # Calculate weighted score
        weighted_score = sum(
            factor_scores[factor] * self.weight_config[factor]
            for factor in ScoreFactors
        )
        
        # Calculate raw score (unweighted average)
        raw_score = sum(factor_scores.values()) / len(factor_scores)
        
        return SearchResultScore(
            raw_score=raw_score,
            weighted_score=weighted_score,
            factor_scores=factor_scores
        )

    def score_search_results(self, results: List[Dict[str, Any]], 
                           search_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score and sort a list of search results.
        
        Args:
            results: List of search results to score
            search_context: Context data for scoring calculations
            
        Returns:
            List[Dict[str, Any]]: Scored and sorted results
        """
        # Calculate context statistics
        prices = [float(r.get("price", 0)) for r in results if r.get("price", 0) > 0]
        search_context = {
            **search_context,
            "avg_price": np.mean(prices) if prices else 0,
            "std_price": np.std(prices) if prices else 0,
            "max_popularity": max((r.get("popularity", 0) for r in results), default=100)
        }
        
        # Score each result
        scored_results = []
        for result in results:
            score = self.score_search_result(result, search_context)
            scored_results.append({
                **result,
                "score": score.weighted_score,
                "score_factors": {
                    factor.value: value 
                    for factor, value in score.factor_scores.items()
                }
            })
        
        # Sort by score
        return sorted(scored_results, key=lambda x: x["score"], reverse=True)