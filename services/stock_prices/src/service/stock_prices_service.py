import logging
from datetime import datetime

from fastapi import WebSocket
from sqlalchemy.future import select

from settings import settings
from libs.pubsub.subscribers import RedisSubscriber
from .database import create_async_session, StockPricesTable, TickersTable
from .pubsub import redis_pubsub_pool


log = logging.getLogger(settings.log_name)


async def get_tickers() -> dict[str, list[dict]]:
    async with create_async_session() as session:
        data = await session.execute(select(TickersTable.ticker))
        tickers = data.scalars().all()
    return {"tickers": tickers}


async def get_stock_history(
    ticker,
    start_dt: datetime,
    end_dt: datetime,
    limit: int
) -> list[dict[str, list]]:
    async with create_async_session() as session:
        query = select(StockPricesTable.price, StockPricesTable.ts). \
            where(StockPricesTable.ticker == ticker). \
            filter(StockPricesTable.ts.between(start_dt, end_dt)). \
            order_by(StockPricesTable.ts.desc()). \
            limit(limit)
        data = await session.execute(query)
        data = data.all()
        ts = [r.ts for r in data]
        prices = [r.price for r in data]
    ret = {
        'ticker': ticker,
        'prices': prices,
        'datetimes': ts
    }
    return ret


async def stock_price_realtime(
    websocket: WebSocket,
    ticker = None,
    default_pubsub_channel = settings.pubsub_channel
):
    pubsub_channel = f'{default_pubsub_channel}.{ticker}' if ticker else default_pubsub_channel
    await websocket.accept()
    subscriber = RedisSubscriber(pubsub_channel, redis_pubsub_pool)
    async for message in subscriber.receive():
        await websocket.send_text(message)
