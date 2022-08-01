import logging
from time import time

import orjson
from redis.asyncio import Redis

from settings import settings
from libs.pubsub.subscribers import RedisSubscriber
from libs.redis_async_timeseries import TimeSeries

DUPLICATE_POLICY = 'last'
RETENTION_PERIOD_SEC = settings.redis_timeseries_retention_period_sec * 1000
LOG = logging.getLogger(settings.log_name)


async def init_redis_timeseries(timeseries: TimeSeries, tickers: list[str]):
    LOG.info('RedisTimeseries init tickers prices')
    for t in tickers:
        try:
            info = await timeseries.info(t)
            if info:
                continue
            await timeseries.create(
                t,
                retention_period=RETENTION_PERIOD_SEC,
                duplicate_policy=DUPLICATE_POLICY
            )
        except Exception as e:
            if 'the key does not exist' not in str(e):
                raise e


async def add_to_redis_ts(redis_timeseries: TimeSeries, stock: dict):
    await redis_timeseries.add(
        key=stock['ticker'],
        value=stock['price'],
        timestamp=stock['timestamp']
    )


async def fill_redis_timeseries():
    channel = settings.pubsub_channel
    host = settings.redis_pubsub_host
    port = settings.redis_pubsub_port
    redis_pubsub = Redis(
        host=host,
        port=port,
    ).pubsub(ignore_subscribe_messages=True)

    host = settings.redis_timeseries_host
    port = settings.redis_timeseries_port
    redis_timeseries = TimeSeries(Redis(
        host=host,
        port=port,
    ))

    tickers = settings.tickers
    LOG.info('Initiating ReidsTimeseries')
    await init_redis_timeseries(redis_timeseries, tickers)
    subscriber = RedisSubscriber(channel, redis_pubsub)
    LOG.info('RedisTimeseries filler start to receiving messages')
    async for message in subscriber.receive():
        stock = orjson.loads(message)
        await add_to_redis_ts(redis_timeseries, stock)
