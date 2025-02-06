from flask_caching import Cache

# Configure Flask-Caching (using simple in-memory cache for now)
cache_config = {
    "CACHE_TYPE": "simple",  # Stores data in memory
    "CACHE_DEFAULT_TIMEOUT": 60  # Cache duration (in seconds)
}

cache = Cache(config=cache_config)
