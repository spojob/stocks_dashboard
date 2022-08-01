import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pydantic import BaseSettings

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
sys.path.append(str(PROJECT_DIR))


def gen_tickers(cnt: int) -> list[int]:
    zeros_c = 2
    tickers = [f'ticker_{str(i).zfill(zeros_c)}' for i in range(cnt)]
    return tickers


class ScrapperSetttings(BaseSettings):
    scrap_interval_sec: int = 1

    redis_timeseries_host = 'redis_timeseries'
    redis_timeseries_port = 6379
    redis_timeseries_retention_period_sec = 60

    redis_pubsub_host = 'redis_pubsub'
    redis_pubsub_port = 6380

    pubsub_channel = 'stocks'

    timescaledb_timeseries_host: str = 'timescaledb_timeseries'
    timescaledb_timeseries_port: int = 5432
    timescaledb_timeseries_user: str = 'postgres'
    timescaledb_timeseries_pass: str = 'password'
    timescaledb_timeseries_db: str = 'postgres'
    timescaledb_prices_table: str = 'prices'
    timescaledb_tickers_table: str = 'tickers'

    pubsub_channel = 'stocks'

    log_level = 'INFO'
    log_name = 'fake_scrapper'
    tickers: list[str] = gen_tickers(100)

    class Config:
        env_prefix = "scrapper_"
        env_file = ".env"


def init_logger(logger_name, log_level=None):
    log_level = log_level.upper() if log_level else 'DEBUG'
    LOGS_DIR = SCRIPT_DIR / 'logs'
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger('root')

    basic_formatter = logging.Formatter(
        '[%(levelname)s - %(name)s - %(asctime)s]: %(message)s')
    verbose_formatter = logging.Formatter(
        '[%(levelname)s - %(name)s - %(asctime)s - %(pathname)s'
        '-%(processName)s[%(process)d] - %(threadName)s[%(thread)d]'
        ': %(message)s]'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(basic_formatter)

    errors_console_handler = logging.StreamHandler(sys.stdout)
    errors_console_handler.setFormatter(verbose_formatter)
    errors_console_handler.setLevel('WARNING')

    file_handler = RotatingFileHandler(
        filename=LOGS_DIR / 'log.txt',
        encoding='utf-8',
        maxBytes=100*1024,
        backupCount=5
    )
    file_handler.setFormatter(basic_formatter)

    errors_file_handler = RotatingFileHandler(
        filename=LOGS_DIR / 'errors.txt',
        encoding='utf-8',
        maxBytes=100*1024,
        backupCount=5
    )
    errors_file_handler.setFormatter(verbose_formatter)
    errors_file_handler.setLevel('WARNING')

    logger.addHandler(console_handler)
    logger.addHandler(errors_console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(errors_file_handler)
    logger.setLevel(log_level)
    logger.propagate = False
    return logger


settings = ScrapperSetttings()
init_logger(settings.log_name, settings.log_level)
