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
   'PRICE': 0.15, # Price weight
   'FLIGHT': 0.60, # Flight weight
   'HOTEL': 0.20, # Hotel weight
   'DESTINATION': 0.05 # Destination weight
}

# Future enhancement:

# region Flight Quality Scoring

# Time-based weights and scoring
JOURNEY_TIME_SCORES = {
   'FLIGHT_DURATION': {  # Hours
       '<2': 100,
       '2-4': 80,
       '4-8': 60,
       '>8': 40
   },
   'LAYOVER': {  # Hours
       '1-2': 100,   # Optimal
       '2-3': 80,    # Good
       '3-4': 60,    # Acceptable  
       '>4': 30      # Long
   }
}

# Enhanced airline scoring
AIRLINE_SCORES = {
   'TIER_1': {
       'score': 100,
       'airlines': ['Emirates', 'Singapore', 'Qatar', 'ANA', 'Etihad'],
       'on_time_min': 0.90,
       'cancellation_max': 0.01
   },
   'TIER_2': {
       'score': 80,
       'airlines': ['United', 'American', 'Delta', 'Lufthansa', 'BA'],
       'on_time_min': 0.85,
       'cancellation_max': 0.02
   },
   'TIER_3': {
       'score': 50,
       'airlines': ['Spirit', 'Frontier', 'Ryanair', 'EasyJet'],
       'on_time_min': 0.75,
       'cancellation_max': 0.03
   }
}

# Enhanced Flight related weights and scoring
AIRCRAFT_SCORES = {
   'WIDE_BODY': {
       'score': 100,
       'types': ['B777', 'A350', 'B787', 'A380', 'A330'],
       'seat_pitch_min': 32,
       'age_max': 12
   },
   'NARROW_BODY': {
       'score': 70,
       'types': ['A320', 'B737', 'A321', 'B738'],
       'seat_pitch_min': 30,
       'age_max': 15
   },
   'REGIONAL': {
       'score': 40,
       'types': ['E190', 'CRJ', 'E170', 'ATR72'],
       'seat_pitch_min': 29,
       'age_max': 18
   }
}

# Airport categories
AIRPORT_SCORES = {
   'MAJOR_HUB': {'score': 100, 'min_routes': 100},
   'REGIONAL_HUB': {'score': 80, 'min_routes': 50},
   'SECONDARY': {'score': 60, 'min_routes': 20}
}

# Comprehensive flight quality weights
FLIGHT_QUALITY_WEIGHTS = {
   'TIME': 0.30,          # Time slot + duration
   'STOPS': 0.20,         # Connection impact
   'AIRLINE': 0.20,       # Carrier quality + performance
   'AIRCRAFT': 0.15,      # Equipment + comfort
   'AIRPORTS': 0.15       # Airport quality
}

# endregion

# region Hotel Quality Scoring
HOTEL_AMENITY_SCORES = {
    'ESSENTIAL': {  # Core amenities
        'WIFI': 20,
        'AC': 15,
        'TV': 10,
        'PRIVATE_BATHROOM': 20
    },
    'LEISURE': {  # Recreation facilities
        'POOL': 15,
        'GYM': 10,
        'SPA': 10,
        'RESTAURANT': 15
    },
    'BUSINESS': {  # Business amenities
        'MEETING_ROOMS': 10,
        'BUSINESS_CENTER': 10,
        'CONFERENCE_FACILITIES': 15
    }
}

HOTEL_LOCATION_SCORES = {
    'CITY_CENTER': 100,
    'BUSINESS_DISTRICT': 80,
    'TOURIST_AREA': 90,
    'AIRPORT': 70,
    'SUBURBAN': 60,
    'REMOTE': 40
}

HOTEL_SERVICE_SCORES = {
    'LUXURY': {'score': 100, 'staff_ratio': 0.8},  # Staff per room
    'UPSCALE': {'score': 80, 'staff_ratio': 0.5},
    'MIDSCALE': {'score': 60, 'staff_ratio': 0.3},
    'ECONOMY': {'score': 40, 'staff_ratio': 0.2}
}

HOTEL_REVIEWS = {
    'CLEANLINESS_WEIGHT': 0.3,
    'SERVICE_WEIGHT': 0.3,
    'LOCATION_WEIGHT': 0.2,
    'VALUE_WEIGHT': 0.2,
    'MINIMUM_REVIEWS': 50
}

HOTEL_AGE_SCORES = {
    'NEW': {'age': 2, 'score': 100},
    'RECENT': {'age': 5, 'score': 90},
    'MAINTAINED': {'age': 10, 'score': 80},
    'HISTORIC': {'age': 50, 'score': 70}
}

# endregion

# region  Destination Quality Scoring
DESTINATION_ACCESSIBILITY = {
    'TRANSPORT_HUB': {'score': 100, 'connections': 50},
    'REGIONAL_CENTER': {'score': 80, 'connections': 30},
    'REMOTE': {'score': 50, 'connections': 10}
}

DESTINATION_SAFETY = {
    'TRAVEL_ADVISORY': {
        'LEVEL_1': 100,  # Exercise normal precautions
        'LEVEL_2': 70,   # Exercise increased caution
        'LEVEL_3': 30,   # Reconsider travel
        'LEVEL_4': 0     # Do not travel
    },
    'CRIME_INDEX': {
        'LOW': 100,
        'MODERATE': 70,
        'HIGH': 30
    },
    'HEALTH_RISK': {
        'LOW': 100,
        'MODERATE': 70,
        'HIGH': 30,
        'SEVERE': 0
    }
}

DESTINATION_ATTRACTIONS = {
    'CULTURAL': {
        'UNESCO_SITES': 20,
        'MUSEUMS': 15,
        'HISTORICAL': 15
    },
    'NATURAL': {
        'PARKS': 15,
        'BEACHES': 15,
        'LANDSCAPES': 15
    },
    'ENTERTAINMENT': {
        'NIGHTLIFE': 10,
        'SHOPPING': 10,
        'DINING': 10
    }
}

DESTINATION_SEASONALITY = {
    'WEATHER': {
        'IDEAL': 100,
        'GOOD': 80,
        'CHALLENGING': 40,
        'EXTREME': 0
    },
    'TOURIST_DENSITY': {
        'LOW': 100,
        'MODERATE': 80,
        'HIGH': 50,
        'OVERCROWDED': 30
    },
    'EVENT_BOOST': {
        'MAJOR_FESTIVAL': 20,
        'SPORTS_EVENT': 15,
        'LOCAL_CELEBRATION': 10
    }
}

# endregion