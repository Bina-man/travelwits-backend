# Travel Search API

A FastAPI-based search engine for finding flight and hotel combinations within a budget.

## Quick Start

1. **Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn

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