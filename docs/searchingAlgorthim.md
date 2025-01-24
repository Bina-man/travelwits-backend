# Multi-Leg Flight Search Algorithm

[![SearchAlgorthim](https://img.shields.io/badge/Config-Python-05122A?style=flat&logo=python)](../app/services/search/trip_search.py)
[![Redis](https://img.shields.io/badge/Cache-Redis-DC382D?style=flat&logo=redis)](../app/services/cache.py)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?style=flat&logo=fastapi)](../app/main.py)

## Core Components

### Route Finding
#### DFS Implementation
- Recursive depth-first search finds all possible routes
- Base cases:
 - Budget exceeded: return empty
 - Destination reached: return current path
- For each unvisited destination:
 - Add flight if within budget
 - Track visited cities to prevent cycles
 - Recursively explore onward paths

#### BFS Alternative
- Queue-based breadth-first search
- Finds shortest paths first
- Better for direct routes
- Less diverse combinations

### Path Generation
- Separate outbound/return path finding
- Budget validation at each step
- Path cost accumulation
- Intermediate city tracking

### Trip Combinations  
- Hotel filtering based on:
 - Destination city
 - Budget constraints  
 - Rating requirements
- Path combination validation:
 - Total cost calculation
 - Maximum stops check
 - Unique combination keys

### Example Routes & Costs
Route | TypePathCostStopsDirectJFK → LAX$1,2901RegionalJFK → LHR → LAX$2,3152ComplexJFK → SYD → LAX → NRT → JFK$4,4004


## Scoring System
- Flight quality factors:
 - Departure times
 - Number of stops
 - Airline ratings
 - Aircraft types
- Hotel quality metrics:
 - Star rating
 - User rating
 - Available amenities

## Example Routes

### Direct (Lowest Cost)
```json
{
 "outbound": "JFK → LAX",
 "return": "LAX → JFK (via DEN)",
 "total_cost": 1290
}
```

### Regional Hub Transfer
```json{
  "outbound": "JFK → LHR → LAX",
  "return": "LAX → JFK (via DEN)",
  "total_cost": 2315
}
```

### Intercontinental
```json{
  "outbound": "JFK → SYD → LAX",
  "return": "LAX → NRT → JFK",
  "total_cost": 4400
}
```

### Optimizations

- Redis caching with TTL
- Early budget pruning
- Path deduplication
- Visited city tracking
- Maximum stops limiting

Future Improvements

- Airline alliance routing
- Mixed-cabin combinations
- Layover duration limits
- Fare class preferences
- Flexible date search
- Airport proximity groups