from sqlalchemy.engine import URL, create_engine
from settings import settings

db_url = URL.create(
    'postgresql+psycopg2',
    username=settings.timescaledb_timeseries_user,
    password=settings.timescaledb_timeseries_pass,
    host=settings.timescaledb_timeseries_host,
    port=settings.timescaledb_timeseries_port,
    database=settings.timescaledb_timeseries_db
)
engine = create_engine(db_url,  pool_pre_ping=True)
