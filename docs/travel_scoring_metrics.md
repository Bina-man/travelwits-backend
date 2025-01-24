# Travel Package Scoring System

## Component Weights
Our scoring system evaluates travel packages using a weighted methodology across four key dimensions:

| Component | Weight | Rationale |
|-----------|---------|-----------|
| Flight | 40% | Primary impact on traveler satisfaction and experience |
| Price | 35% | Critical factor for value and budget considerations |
| Hotel | 20% | Important for stay quality but more flexible than transport |
| Destination | 5% | Market demand indicator with subjective preference |

## Flight Scoring (40%)
Flight quality is scored based on departure times and stops:

### Departure Time Scoring
| Time Window | Score | Rationale |
|------------|--------|-----------|
| 8:00-11:00 | 100 | Peak morning - Optimal business hours, reliable |
| 11:00-16:00 | 80 | Midday - Good for leisure, flexible |
| 6:00-8:00 | 60 | Early morning - Less convenient but reliable |
| 16:00-21:00 | 50 | Evening - Higher delay risk |
| Other | 20 | Off hours - Night flights, very early morning |

### Stop Penalties
- Each stop reduces score by 40 points
- Prioritizes direct flights
- Reflects connection risks and travel time

## Hotel Scoring (20%)
Score calculated using weighted metrics:
```python
hotel_score = min(100, (
    stars * 18 +          # Base quality indicator
    rating * 10 +         # User satisfaction weight
    amenities_count * 7   # Additional features value
))
```

### Weights Rationale
- Stars (18x): Primary quality baseline
- Ratings (10x): Real guest experience
- Amenities (7x): Added value features

## Price Scoring (35%)
Evaluated against market context:
```python
price_score = max(0, 100 * (1 - (total_cost / max_cost))) * 1.5
```

Where:
- `total_cost` = flights + (hotel_per_night * nights)
- `max_cost` = (max_flight_price * 2) + (max_hotel_price * nights)
- 1.5x multiplier to reward exceptional value

## Destination Scoring (5%)
Based on market data:
- Uses destination popularity metrics
- Scaled to 0-100 range
- Reflects seasonal demand

## Final Score Calculation
1. Calculate component scores (0-100 range)
2. Apply component weights
3. Apply 1.2x final multiplier
4. Round to 2 decimal places

Example:
```python
final_score = (
    (flight_score * 0.40) +
    (price_score * 0.35) +
    (hotel_score * 0.20) +
    (destination_score * 0.05)
) * 1.2
```

## Score Ranges
| Range | Interpretation |
|-------|----------------|
| 90-100 | Exceptional value - Premium offering |
| 80-89 | Strong recommendation - High value |
| 70-79 | Good option - Recommended |
| 60-69 | Acceptable - Consider alternatives |
| <60 | Not recommended - Review components |

## Implementation Notes
- All component scores normalized to 0-100 before weighting
- Negative scores capped at 0
- Final scores capped at 100 after multiplier
- Rounding ensures consistent display