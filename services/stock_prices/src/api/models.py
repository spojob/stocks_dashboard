from pydantic import BaseModel
from datetime import datetime


class TickersModel(BaseModel):
    tickers: list[str]


class StockHistoryModel(BaseModel):
    ticker: str
    prices: list[int]
    datetimes: list[datetime]
