import os

from flask_caching import Cache

cache = Cache(
    config={
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": os.getenv("CACHE_REDIS_HOST", "redis"),
        "CACHE_REDIS_PORT": os.getenv("CACHE_REDIS_PORT", 6379),
        "CACHE_REDIS_DB": os.getenv("CACHE_REDIS_DB", 0),
    }
)
