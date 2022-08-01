from redis.asyncio import Redis
from settings import settings

redis_pubsub_pool = Redis(
        host=settings.redis_pubsub_host,
        port=settings.redis_pubsub_port,
).pubsub(ignore_subscribe_messages=True)