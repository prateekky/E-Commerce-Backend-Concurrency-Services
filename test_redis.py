from app.core.redis import redis_client

redis_client.set("name", "Prateek")

print(redis_client.get("name"))
