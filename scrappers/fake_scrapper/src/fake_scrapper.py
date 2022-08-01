from time import time
from random import random
from asyncpg.pool import Pool

from settings import settings
from redis.exceptions import ResponseError
from libs.redis_async_timeseries import TimeSeries

PRICES_TABLE = settings.timescaledb_prices_table

def generate_movement() -> int:
    movement = -1 if random() < 0.5 else 1
    return movement


def generate_new_price(price: int) -> int:
    movement = generate_movement()
    price += movement
    if price < 0:
        price = 0
    return price


class FakePriceScrapper:
    def __init__(
        self,
        redis_timeseries: TimeSeries,
        timescaledb_timeseries: Pool
    ) -> None:
        self.redis_timeseries = redis_timeseries
        self.timescaledb_timeseries = timescaledb_timeseries

    async def get_latest_price(self, ticker) -> int:
        try:
            timestamp, price = await self.redis_timeseries.get(ticker)
        except ResponseError as e:
            if 'TSDB: the key does not exist' == str(e):
                try:
                    async with self.timescaledb_timeseries.acquire() as conn:
                        q = f"""
                            SELECT * FROM {PRICES_TABLE}
                            WHERE ticker=$1
                            ORDER BY ts DESC LIMIT 1;
                        """
                        rows = await conn.fetch(q, ticker)
                        await conn.close()
                        if rows:
                            row = rows[0] 
                        price = row['price']
                except Exception as e1:
                    raise e1
            else:
                raise e
        price = generate_new_price(price)
        return price

    async def get_latest_stock_status(self, ticker) -> dict:
        price = await self.get_latest_price(ticker)
        timestamp = int(time())
        stock = {
            'ticker': ticker,
            'price': price,
            'timestamp': timestamp
        }
        return stock
