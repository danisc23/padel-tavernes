import os

PT_ENV = os.getenv("PT_ENV", "dev")
PT_ALLOWED_ORIGINS = ["*"] if PT_ENV == "dev" else os.getenv("PT_ALLOWED_ORIGINS", "").split(",")

CACHE_REDIS_HOST = os.getenv("CACHE_REDIS_HOST", "redis")
CACHE_REDIS_PORT = os.getenv("CACHE_REDIS_PORT", 6379)
CACHE_REDIS_DB = os.getenv("CACHE_REDIS_DB", 0)

LOCATION_IQ_API_KEY = os.getenv("LOCATION_IQ_API_KEY")
