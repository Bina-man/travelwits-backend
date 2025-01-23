from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from .api.routes import router, TravelAPI


def setup_logging():
    """
    Configure application-wide logging settings.
    
    Creates a logs directory and sets up both file and console logging handlers.
    File logging uses rotation to manage disk space.
    
    File Handler: Detailed DEBUG level logs with rotation
    Console Handler: Basic INFO level logs
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path(__file__).resolve().parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler with INFO level
            logging.StreamHandler(),
            # File handler with DEBUG level for more details
            RotatingFileHandler(
                logs_dir / "travel_search.log",
                maxBytes=10485760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Travel Search API",
    description="API for searching and booking multi-city travel packages",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)
from .services.stats import SearchStats

@app.on_event("startup")
async def startup_event():
    """
    Initialize application services on startup.
    
    Performs the following tasks:
    1. Loads flight and hotel data from JSON files
    2. Initializes the statistics collector
    3. Sets up the Travel API service
    
    Raises:
        FileNotFoundError: If data files are missing
        JSONDecodeError: If data files contain invalid JSON
    """
    try:
        # Get the base directory path
        base_dir = Path(__file__).resolve().parent.parent
        
        # Load data files using absolute paths
        logger.debug(f"Loading flights from {base_dir / 'data' / 'flights.json'}")
        with open(base_dir / "data" / "flights.json") as f:
            flights = json.load(f)
        logger.info(f"Loaded {len(flights)} flights")
        
        logger.debug(f"Loading hotels from {base_dir / 'data' / 'hotels.json'}")
        with open(base_dir / "data" / "hotels.json") as f:
            hotels = json.load(f)
        logger.info(f"Loaded {len(hotels)} hotels")

        # Initialize services
        router.stats = SearchStats()
        logger.info("Successfully initialized Stats Collector")
        
        router.travel_api = TravelAPI(flights, hotels)
        logger.info("Successfully initialized Travel API")
        
    except FileNotFoundError as e:
        logger.error(f"Error: Could not find data files - {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error: Invalid JSON in data files - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)