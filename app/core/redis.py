import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

CACHE_ALL_PRODUCTS = "all_products"
CACHE_TIME = 300