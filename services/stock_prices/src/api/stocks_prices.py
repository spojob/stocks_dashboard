from fastapi import APIRouter, WebSocket

from typing import Optional
from datetime import datetime

from service import get_tickers, get_stock_history, stock_price_realtime
from .models import TickersModel, StockHistoryModel
from settings import settings

router = APIRouter(
    prefix="/api/stocks"
)


@router.get('/tickers', response_model=TickersModel)
async def get_tickers_():
    return await get_tickers()


@router.get('/{ticker}', response_model=StockHistoryModel)
async def get_stock_history_(
        ticker,
        limit: Optional[int] = 100,
        start_dt: Optional[datetime] = None,
        end_dt: Optional[datetime] = None
):
    start_dt = start_dt if start_dt else datetime(1, 1, 1)
    end_dt = end_dt if end_dt else datetime.now()
    return await get_stock_history(ticker, start_dt, end_dt, limit)


@router.websocket('/ws')
async def websocket(
        websocket: WebSocket,
        ticker: Optional[str] = None
):
    await stock_price_realtime(websocket, ticker)
