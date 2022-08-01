from re import I
import sys
import logging
from asyncio import run, create_task, gather, sleep

import orjson
import asyncpg
from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from settings import settings
from fake_scrapper import FakePriceScrapper
from libs.pubsub.publishers import IPublisher, RedisPublisher
from libs.redis_async_timeseries import TimeSeries


LOG = logging.getLogger(settings.log_name)


def create_publishers(base_channel, tickers: list[str], redis_pubsub: PubSub):
    publishers = [
        {
            'ticker': ticker,
            "publishers":   (
                RedisPublisher(f'{base_channel}.{ticker}', redis_pubsub),
                RedisPublisher(base_channel, redis_pubsub)
            )
        }
        for ticker in tickers
    ]
    return publishers


async def publish_task(scrapper: FakePriceScrapper, publishers: list[IPublisher], ticker):
    stock = await scrapper.get_latest_stock_status(ticker)
    msg = orjson.dumps(stock)
    await gather(*[p.publish(msg) for p in publishers])


def create_tasks(publishers: dict, scrapper: FakePriceScrapper):
    tasks = []
    for p in publishers:
        ticker = p['ticker']
        pubs = p['publishers']
        coro = publish_task(scrapper, pubs, ticker)
        tasks.append(create_task(coro))
    return tasks


async def main():
    host = settings.redis_pubsub_host
    port = settings.redis_pubsub_port
    LOG.info(f'Connecting RedisPubsub "{host}:{port}"')
    redis_pubsub = Redis(
        host=host,
        port=port
    ).pubsub(ignore_subscribe_messages=True)

    host = settings.redis_timeseries_host
    port = settings.redis_timeseries_port
    LOG.info(f'Connecting RedisTimeseries "{host}:{port}"')
    redis_timeseries = TimeSeries(Redis(
        host=host,
        port=port,
    ))

    host = settings.timescaledb_timeseries_host
    port = settings.timescaledb_timeseries_port
    user = settings.timescaledb_timeseries_user
    passw = settings.timescaledb_timeseries_pass
    db = settings.timescaledb_timeseries_db
    LOG.info(F'Connecting timescaledb timeseries ""{host}:{port}""')
    timescaledb_conn = await asyncpg.create_pool(
        host=host,
        port=port,
        user=user,
        password=passw,
        database=db,
    )
    tickers = settings.tickers
    LOG.info(
        'Following tickers will be scrapped:\n'+'\n'.join(tickers)
    )

    channel = settings.pubsub_channel
    publishers = create_publishers(channel, tickers, redis_pubsub)
    scrap_interval_sec = settings.scrap_interval_sec
    scrapper = FakePriceScrapper(
        redis_timeseries,
        timescaledb_conn
    )
    LOG.info(
        f'Start publishing stocks info to {channel}, and {channel}.[ticker]'
    )
    scrap_interval_sec = 1
    while True:
        tasks = create_tasks(publishers, scrapper)
        await gather(*tasks)
        await sleep(scrap_interval_sec)


if __name__ == '__main__':
    run(main())
