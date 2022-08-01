
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.engine import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from settings import settings

from typing import Callable

db_url = URL.create(
    'postgresql+asyncpg',
    username=settings.timescaledb_timeseries_user,
    password=settings.timescaledb_timeseries_pass,
    host=settings.timescaledb_timeseries_host,
    port=settings.timescaledb_timeseries_port,
    database=settings.timescaledb_timeseries_db
)
engine = create_async_engine(db_url,  pool_pre_ping=True)
create_async_session: Callable[[], AsyncSession] = sessionmaker(
    engine, 
    class_=AsyncSession
)

Base = declarative_base()


class StockPricesTable(Base):
    __tablename__ = 'prices'
    ticker = Column(String)
    price = Column(Integer)
    ts = Column(Date, primary_key=True)


class TickersTable(Base):
    __tablename__ = 'tickers'
    ticker = Column(String, primary_key=True)
