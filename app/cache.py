from flask_caching import Cache

from app.settings import CACHE_REDIS_DB, CACHE_REDIS_HOST, CACHE_REDIS_PORT

cache = Cache(
    config={
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": CACHE_REDIS_HOST,
        "CACHE_REDIS_PORT": CACHE_REDIS_PORT,
        "CACHE_REDIS_DB": CACHE_REDIS_DB,
    }
)
