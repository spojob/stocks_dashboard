from asyncio import run
import logging
from time import time
from datetime import datetime

import orjson
import asyncpg
from asyncpg.connection import Connection
from redis.asyncio import Redis

from settings import settings
from libs.pubsub.subscribers import RedisSubscriber

LOG = logging.getLogger(settings.log_name)


async def init_timescaledb_timeseries(db_conn: Connection, tickers: list[str]):
    prices_table = settings.timescaledb_prices_table
    tickers_table = settings.timescaledb_tickers_table
    create_script = f"""
    CREATE TABLE IF NOT EXISTS "{prices_table}" (
        ts TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        price INTEGER NOT NULL,
        ticker TEXT NOT NULL
    );

    SELECT create_hypertable(
        '{prices_table}',
        'ts',
        create_default_indexes => FALSE,
        if_not_exists => TRUE
    );

    CREATE INDEX IF NOT EXISTS "{prices_table}_ticker_ts" ON prices (ticker, ts DESC);

    CREATE TABLE IF NOT EXISTS "{tickers_table}" (
        ticker TEXT PRIMARY KEY
    );
    """
    LOG.info('TimescaleDB init price, tickers table')
    queries = [ q.strip() for q in create_script.split(';') if q.strip() ]
    for q in queries:
        await db_conn.execute(q)
    absent = []
    for t in tickers:
        q = f"""
                SELECT 1
                FROM "{tickers_table}"
                WHERE ticker = $1 limit 1;
        """
        r = await db_conn.fetch(q, t)
        if r:
            continue
        absent.append(t)
    if not absent:
        return
    async with db_conn.transaction():
        ts = datetime.fromtimestamp(int(time()))
        q = f"""
        INSERT INTO "{prices_table}" (ticker, price, ts)
        VALUES ($1, 0, $2);
        """
        rows = [(t,ts) for t in absent]
        LOG.info('TimescaleDB filling price table initial data')
        await db_conn.executemany(q, rows)
        q = f"""
        INSERT INTO {tickers_table} (ticker)
        VALUES ($1);
        """
        rows = [(t,) for t in absent]
        LOG.info('TimescaleDB tickers table initial data')
        await db_conn.executemany(q, rows)



async def add_to_quest_db_ts(db_conn: Connection, stock: dict):
    query = f"""
    INSERT INTO prices (ticker, price, ts) 
    VALUES ($1, $2, $3)
    """
    async with db_conn.transaction():
        await db_conn.execute(
            query, 
            stock['ticker'], 
            stock['price'], 
            datetime.fromtimestamp(stock['timestamp'])
        )


async def fill_timescaledb_timeseries():
    channel = settings.pubsub_channel
    host = settings.redis_pubsub_host
    port = settings.redis_pubsub_port
    redis_pubsub = Redis(
        host=host,
        port=port,
    ).pubsub(ignore_subscribe_messages=True)

    host = settings.timescaledb_timeseries_host
    port = settings.timescaledb_timeseries_port
    user = settings.timescaledb_timeseries_user
    passw = settings.timescaledb_timeseries_pass
    db = settings.timescaledb_timeseries_db
    timescaledb_con = await asyncpg.connect(
        host=host,
        port=port,
        user=user,
        password=passw,
        database=db
    )

    tickers = settings.tickers
    LOG.info('Initiating timescaledbTimeseries')
    await init_timescaledb_timeseries(timescaledb_con, tickers)
    subscriber = RedisSubscriber(channel, redis_pubsub)
    LOG.info('timescaledb filler start to receiving messages')
    async for message in subscriber.receive():
        stock = orjson.loads(message)
        await add_to_quest_db_ts(timescaledb_con, stock)
