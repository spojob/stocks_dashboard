from fastapi import APIRouter

from .stocks_prices import router as stock_prices_router

router = APIRouter()
router.include_router(stock_prices_router)
