from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# File Paths
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

# API Configuration
API_TITLE = "Travel Search API"
API_DESCRIPTION = "API for searching and booking multi-city travel packages"
API_VERSION = "1.0.0"

# Search Configuration
MAX_SEARCH_RESULTS = 50
MIN_NIGHTS = 1
MAX_NIGHTS = 30
AIRPORT_CODE_LENGTH = 3

# Scoring Weights
SCORING_WEIGHTS = {
    'price': 0.35,
    'comfort': 0.35,
    'convenience': 0.30
}

MULTI_CITY_SCORING_WEIGHTS = {
    'price': 0.4,
    'flight': 0.3,
    'hotel': 0.3
}

# Flight Scoring Configuration
FLIGHT_BASE_SCORE = 10.0
FLIGHT_STOP_PENALTY = 2.0
PREFERRED_DEPARTURE_START = 8  # 8 AM
PREFERRED_DEPARTURE_END = 20   # 8 PM
PREFERRED_DEPARTURE_BONUS = 2.0

# Hotel Scoring Configuration
HOTEL_AMENITY_SCORE = 0.5
PRICE_EFFICIENCY_FACTOR = 1000

# Seasonality Scores
SEASONALITY_SCORES = {
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

# Search Engine Configuration
SEARCH_FACTORS_WEIGHTS = {
    'PRICE_EFFICIENCY': 0.4,
    'FLIGHT_QUALITY': 0.25,
    'HOTEL_RATING': 0.25,
    'DESTINATION_POPULARITY': 0.1,
}

# CORS Configuration
CORS_SETTINGS = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# Scoring Constants
SCORE_WEIGHTS = {
    'price': 0.3,
    'flight': 0.5,
    'hotel': 0.2
}

FLIGHT_TIME_SCORES = {
    'prime_time': 100,    # 8:00-11:00
    'decent_time': 85,    # 11:00-16:00
    'early_morning': 70,  # 6:00-8:00
    'evening': 60,        # 16:00-21:00
    'off_hours': 40      # 21:00-6:00
}

FLIGHT_HOURS = {
    'prime_start': 8,
    'prime_end': 11,
    'decent_end': 16,
    'early_start': 6,
    'evening_end': 21
}

STOP_PENALTY = 30  # Points deducted per stop

HOTEL_SCORE_FACTORS = {
    'star_multiplier': 15,    # 15 points per star
    'rating_multiplier': 5,   # 5 points per rating point
    'amenity_points': 5       # 5 points per amenity
} 