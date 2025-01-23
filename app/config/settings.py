from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# API Settings
AIRPORT_CODE_LENGTH = 3
MIN_NIGHTS = 1
MAX_NIGHTS = 14
MAX_SEARCH_RESULTS = 10

# File Paths
FLIGHTS_FILE = DATA_DIR / "data/flights.json"
HOTELS_FILE = DATA_DIR / "data/hotels.json"

# Cache Settings
REDIS_URL = "redis://localhost:6379"
DEFAULT_CACHE_TTL = 3600  # 1 hour 