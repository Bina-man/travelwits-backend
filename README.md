# Travel Search API

A FastAPI-based search engine for finding flight and hotel combinations within a budget.

## Local documentations 
These are important parts of my work ...

[![Search Algorithm](https://img.shields.io/badge/Search-Algorithm-blue?style=flat&logo=python)](./docs/searchingAlgorthim.md)
[![Caching System](https://img.shields.io/badge/Cache-System-red?style=flat&logo=redis)](./docs/config.md) 
[![Travel Metrics](https://img.shields.io/badge/Travel-Metrics-green?style=flat&logo=fastapi)](./docs/travel_scoring_metrics.md)
## Quick Start

1. **Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn

# Start Redis
brew services start redis

# Run the server
uvicorn app.main:app --reload
```

2. **Sample API Call**
```
GET /search?origin=JFK&nights=3&budget=2000
```

## Project Structure
```
.
├── app/                  # Main application code
│   ├── api/             # API endpoints
│   ├── models/          # Data models
│   ├── services/        # Business logic
│   └── main.py         # App entry point
└── data/               # JSON data files
    ├── flights.json
    └── hotels.json
```

## API Endpoints

### Search Trips
- **URL**: `/search`
- **Method**: GET
- **Parameters**:
  - `origin`: Airport code (e.g., JFK)
  - `nights`: Number of nights (1-30)
  - `budget`: Maximum total budget

## Data Files
Place your JSON data files in the `data/` directory:
- `flights.json`: Flight data
- `hotels.json`: Hotel data