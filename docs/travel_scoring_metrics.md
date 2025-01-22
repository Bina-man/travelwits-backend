# Travel Package Scoring Factors and Weights

## Summary Table
| Category | Factor | Weight | What it Measures | Real Examples with Scores |
|----------|---------|---------|-----------------|------------------------|
| **Core Pricing** | Value for Money | 15% | - Price vs market average<br>- Included amenities<br>- Location value<br>- Package benefits | High (0.9): $200 hotel in $300 market with breakfast<br>Low (0.4): $200 hotel with no amenities |
| | Price Stability | 10% | - Historical price changes<br>- Seasonal variations<br>- Pricing predictability<br>- Cross-platform consistency | High (0.85): NYC-London $800±$50<br>Low (0.3): NYC-Paris $500-1200 range |
| | Cost Transparency | 10% | - Upfront pricing<br>- Hidden fees<br>- Additional charges<br>- Tax inclusion | High (0.95): All-inclusive with no hidden fees<br>Low (0.4): Hidden resort fees and taxes |
| **Quality** | Accommodation | 10% | - Star rating<br>- Amenities<br>- Location<br>- Reviews | High (0.85): New 4-star, central location<br>Low (0.45): Old 3-star, poor location |
| | Transportation | 10% | - Flight type<br>- Airline rating<br>- Transfer quality<br>- Timing | High (0.9): Direct flight, private transfer<br>Low (0.4): Multiple stops, public transport |
| | Service Level | 5% | - Support hours<br>- Response time<br>- Languages<br>- Problem resolution | High (0.9): 24/7 multilingual support<br>Low (0.4): Limited email-only support |
| **Destination** | Seasonal Fit | 7% | - Weather<br>- Events<br>- Peak periods<br>- Activities availability | High (0.95): Caribbean in perfect season<br>Low (0.3): Monsoon season in Asia |
| | Infrastructure | 7% | - Local transport<br>- Medical facilities<br>- Tourist services<br>- Safety | High (0.95): Singapore's modern facilities<br>Low (0.4): Remote area limited services |
| | Cultural Value | 6% | - Attractions<br>- Local experiences<br>- Entertainment<br>- History | High (0.9): Rome historic center<br>Low (0.3): Airport hotel area |
| **Customer Fit** | Demographic Match | 8% | - Target audience fit<br>- Age suitability<br>- Activity level<br>- Special needs | High (0.95): Family resort for families<br>Low (0.2): Party hotel for families |
| | Booking Pattern | 7% | - Historical success<br>- Satisfaction rates<br>- Repeat bookings<br>- Complaints | High (0.9): Popular route, high satisfaction<br>Low (0.4): New route, mixed reviews |
| | Flexibility | 5% | - Cancellation terms<br>- Change policy<br>- Refund options<br>- Rebooking fees | High (0.9): Free cancellation 24h before<br>Low (0.3): Non-refundable, no changes |

Note: Each factor's score ranges from 0-1, where 1 is best. Final package score is sum of all weighted scores.

## Core Pricing Factors (Total: 35%)

### Value for Money (Weight: 15% = 0.15)
**What it means:** How much total value a customer gets relative to the money spent
**Impact on Final Score:** Can contribute up to 0.15 to final score (15% of total)

**Examples in action:**
```
Hotel A: $300/night (Manhattan)
- Includes: Breakfast ($30), Airport transfer ($60), WiFi ($15)
- Near major attractions (saves $30/day in transport)
- Total value: $435/day for $300
Raw Score: 0.90 (excellent value)
Weighted Score: 0.90 * 0.15 = 0.135 towards final score

Hotel B: $200/night (Manhattan)
- No inclusions
- 30 minutes from attractions ($30/day transport needed)
- Extra costs for everything
Raw Score: 0.40 (poor value)
Weighted Score: 0.40 * 0.15 = 0.06 towards final score
```

### Price Stability (Weight: 10% = 0.10)
**What it means:** How reliable and predictable the price remains over time
**Impact on Final Score:** Can contribute up to 0.10 to final score (10% of total)

**Examples in action:**
```
Route A: NYC to London
- Summer price range: $800-850
- Winter price range: $600-650
- Predictable seasonal changes
Raw Score: 0.85 (very stable)
Weighted Score: 0.85 * 0.10 = 0.085 towards final score

Route B: NYC to Paris
- Summer price range: $500-1200
- Winter price range: $400-900
- Highly unpredictable
Raw Score: 0.30 (unstable)
Weighted Score: 0.30 * 0.10 = 0.03 towards final score
```

### Cost Transparency (Weight: 10% = 0.10)
**What it means:** Clarity and completeness of pricing information
**Impact on Final Score:** Can contribute up to 0.10 to final score (10% of total)

**Examples in action:**
```
Package A: All-Inclusive Resort
- All taxes and fees shown upfront
- Meal plan clearly defined
- No hidden charges
Raw Score: 0.95 (highly transparent)
Weighted Score: 0.95 * 0.10 = 0.095 towards final score

Package B: Budget Hotel
- Base rate advertised
- Resort fee hidden
- Additional taxes not shown
Raw Score: 0.40 (poor transparency)
Weighted Score: 0.40 * 0.10 = 0.04 towards final score
```

## Quality Metrics (Total: 25%)

### Accommodation (Weight: 10% = 0.10)
**What it means:** Overall quality and reliability of the lodging
**Impact on Final Score:** Can contribute up to 0.10 to final score (10% of total)

**Examples in action:**
```
Hotel A in Barcelona:
- 2-year-old renovation
- 24/7 front desk
- Premium location
Raw Score: 0.85 (excellent)
Weighted Score: 0.85 * 0.10 = 0.085 towards final score

Hotel B in Barcelona:
- Needs renovation
- Limited service
- Poor location
Raw Score: 0.45 (below average)
Weighted Score: 0.45 * 0.10 = 0.045 towards final score
```

### Transportation (Weight: 10% = 0.10)
**What it means:** Quality of all travel components
**Impact on Final Score:** Can contribute up to 0.10 to final score (10% of total)

**Examples in action:**
```
Package A Transport:
- Direct flight, new aircraft
- Private transfer
Raw Score: 0.90 (excellent)
Weighted Score: 0.90 * 0.10 = 0.09 towards final score

Package B Transport:
- Multiple stops, old aircraft
- Public transfer
Raw Score: 0.40 (poor)
Weighted Score: 0.40 * 0.10 = 0.04 towards final score
```

### Service Level (Weight: 5% = 0.05)
**What it means:** Quality of customer support and service
**Impact on Final Score:** Can contribute up to 0.05 to final score (5% of total)

**Examples in action:**
```
Provider A:
- 24/7 support
- Multiple languages
- Quick response time
Raw Score: 0.90 (excellent)
Weighted Score: 0.90 * 0.05 = 0.045 towards final score

Provider B:
- Limited hours
- Email only
- Slow response
Raw Score: 0.40 (poor)
Weighted Score: 0.40 * 0.05 = 0.02 towards final score
```