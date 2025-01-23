# Trip Package Scoring System

The Trip Package Scoring System evaluates travel packages on a 0-100 scale by considering four key components:

## Components and Weights

### Price Efficiency (35%)
- Evaluates cost-effectiveness relative to budget
- Score = 100 * (1 - total_cost/budget) * 0.35
- Example: $1500/$2000 budget = 25% savings = 75 points * 0.35 = 26.25 points

### Flight Quality (40%)
Scores based on departure times and stops:
- Prime hours (8:00-11:00): 100 points
- Business hours (11:00-16:00): 80 points
- Early morning (6:00-8:00): 60 points
- Evening (16:00-21:00): 50 points
- Night/Off-hours: 20 points
- Stop penalty: -40 points per stop

Final flight score = Average of outbound and return scores * 0.40

### Hotel Quality (20%)
Calculated using:
- Stars: 18 points per star
- Guest Rating: 10 points per rating point
- Amenities: 7 points per amenity
Maximum 100 points * 0.20

### Destination Popularity (5%)
Based on route frequency as percentage of total flights * 0.05

## Final Score Calculation
1. Sum all weighted component scores
2. Apply scaling factor of 1.2
3. Final score = (Sum of components) * 1.2

## Score Ranges
- Excellent: 85-100
- Good: 70-84
- Average: 55-69
- Poor: <55

## Example Calculation

For a $2000 budget, 5-night JFK-LAX trip:
```
Trip Details:
- Outbound: 8am non-stop flight ($409)
- Return: 8am non-stop flight ($459)
- Hotel: 4-star, 7/10 rating, 3 amenities ($150/night)
Total cost: $1618

Price Score: ($2000-$1618)/$2000 = 0.19 * 100 * 0.35 = 6.65
Flight Score: (100 + 100)/2 * 0.40 = 40
Hotel Score: (72 + 70 + 21) * 0.20 = 17
Popularity Score: 100 * 0.05 = 5

Raw Score: 68.65
Final Score: 68.65 * 1.2 = 82.38 (Good)
```