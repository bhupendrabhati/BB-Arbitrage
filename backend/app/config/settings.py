from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import Field


class TradingMode(str, Enum):
    SCANNER = "scanner"
    PAPER = "paper"
    LIVE = "live"


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_NAME: str = "BB-ARBITRAGE"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://bbuser:bbpass@localhost:5432/bb_arbitrage"
    REDIS_URL: str = "redis://localhost:6379/0"

    TRADING_MODE: TradingMode = TradingMode.PAPER

    INITIAL_CAPITAL_INR: float = 10000.0
    MAX_TRADE_AMOUNT_INR: float = 5000.0
    MAX_DAILY_LOSS_INR: float = 500.0
    MAX_OPEN_TRADES: int = 1
    MAX_TRADES_PER_DAY: int = 5

    MIN_NET_PROFIT_INR: float = 0.10
    MIN_NET_PROFIT_PERCENT: float = 0.01

    MAX_SLIPPAGE_PERCENT: float = 0.05
    STALE_DATA_MS: int = 500

    LIVE_TRADING_ENABLED: bool = False

    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    COINBASE_API_KEY: str = ""
    COINBASE_API_SECRET: str = ""
    KRAKEN_API_KEY: str = ""
    KRAKEN_API_SECRET: str = ""

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ALERT_EMAIL: str = ""

    PROMETHEUS_ENABLED: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
