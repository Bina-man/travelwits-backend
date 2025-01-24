"""
Travel Search Application Configuration

Config categories:
- Paths and Files
- Logging
- Cache
- Search Parameters 
- Travel Scoring
"""

from pathlib import Path

# Base Paths & Files
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

FLIGHTS_FILE = DATA_DIR / "flights.json"
HOTELS_FILE = DATA_DIR / "hotels.json"
LOG_FILE = LOGS_DIR / "travel_search.log"

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = "DEBUG"
LOG_FILE_MAX_BYTES = 10485760  # 10MB
LOG_FILE_BACKUP_COUNT = 5

# Cache Configuration
REDIS_URL = "redis://localhost:6379/0"
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Search Parameters
MAX_SEARCH_RESULTS = 50  # Maximum number of search results
MIN_NIGHTS = 1  # Minimum nights
MAX_NIGHTS = 30  # Maximum nights
AIRPORT_CODE_LENGTH = 3  # IATA format https://airportcodes.aero/
MIN_CUSTOMER_SPENDING = 0

# Hotel Configuration
HOTEL_STAY = {
   'MIN_NIGHTS': 1, 
   'MAX_NIGHTS': 30
}

HOTEL_WEIGHTS = {
  'STARS_MULTIPLIER': 18,
  'RATING_MULTIPLIER': 10,
  'AMENITY_MULTIPLIER': 7
}
MAX_HOTEL_SCORE = 100

# Flight Configuration
FLIGHT_TIME_SCORES = {
  'PEAK_MORNING': (8, 11, 100),    # 8-11am: ideal time
  'MIDDAY': (11, 16, 80),          # 11am-4pm: good time
  'EARLY_MORNING': (6, 8, 60),     # 6-8am: ok time
  'EVENING': (16, 21, 50),         # 4-9pm: less ideal
  'OFF_HOURS': (0, 24, 20)         # All other times
}
STOP_PENALTY = 40 # Penalty for each stop

# Scoring Weights
SCORING_WEIGHTS = {
   'PRICE': 0.35, # Price weight
   'FLIGHT': 0.40, # Flight weight
   'HOTEL': 0.20, # Hotel weight
   'DESTINATION': 0.05 # Destination weight
}