# Travel Search Scoring System

## Machine Learning-Inspired Design
Our scoring system implements a weighted ranking model inspired by ML techniques:

[![ConfigPath](https://img.shields.io/badge/Config-Python-05122A?style=flat&logo=python)](../app/config/config.py)

```python
SCORING_WEIGHTS = {
    'PRICE': 0.35,
    'FLIGHT': 0.40,
    'HOTEL': 0.20,
    'DESTINATION': 0.05
}
```

## Component Scoring Logic

### Flight Time Scoring
```python
FLIGHT_TIME_SCORES = {
    'PEAK_MORNING': (8, 11, 100),  # Highest demand window
    'MIDDAY': (11, 16, 80),        # Standard preference
    'EARLY_MORNING': (6, 8, 60),   # Lower preference
    'EVENING': (16, 21, 50),       # Reduced demand
    'OFF_HOURS': (0, 24, 20)       # Lowest preference
}
STOP_PENALTY = 40
```

### Hotel Quality Model
```python
HOTEL_WEIGHTS = {
    'STARS_MULTIPLIER': 18,     # Base quality predictor
    'RATING_MULTIPLIER': 10,    # User satisfaction metric
    'AMENITY_MULTIPLIER': 7     # Service level indicator
}
```

## Performance Optimization
```python
DEFAULT_CACHE_TTL = 3600  # Cache duration
MAX_SEARCH_RESULTS = 50   # Results limit
```

## Future Enhancements

1. Flight Quality Scoring
   - Journey duration and layover scoring
   - Airline tier classification
   - Aircraft type evaluation
   - Airport hub ranking
   - Flight quality weighted scoring

2. Hotel Quality Enhancement
   - Essential and luxury amenity scoring
   - Location-based evaluation
   - Service level classification
   - Review-based weighting system
   - Property age consideration

3. Real-time Price Sensitivity
   - Demand-based multipliers
   - Competition adjustment factors
   - Time-based pricing
   - Market condition responses
   - Dynamic pricing thresholds