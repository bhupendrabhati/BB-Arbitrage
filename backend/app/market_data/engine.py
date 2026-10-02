import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Optional
from app.exchanges.base import ExchangeAdapter, Ticker, OrderBook
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("market_data")


class MarketDataEngine:
    def __init__(self, stale_threshold_ms: int | None = None):
        self.stale_threshold_ms = stale_threshold_ms or settings.STALE_DATA_MS
        self._tickers: dict[str, dict[str, Ticker]] = {}
        self._order_books: dict[str, dict[str, OrderBook]] = {}
        self._last_update: dict[str, dict[str, datetime]] = {}
        self._exchanges: dict[str, ExchangeAdapter] = {}
        self._running = False
        self._tasks: list[asyncio.Task] = []

    def register_exchange(self, name: str, adapter: ExchangeAdapter) -> None:
        self._exchanges[name] = adapter
        self._tickers[name] = {}
        self._order_books[name] = {}
        self._last_update[name] = {}

    async def start(self) -> None:
        self._running = True
        for name, adapter in self._exchanges.items():
            task = asyncio.create_task(self._poll_exchange(name, adapter))
            self._tasks.append(task)
        logger.info("market_data_engine_started", exchanges=list(self._exchanges.keys()))

    async def stop(self) -> None:
        self._running = False
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("market_data_engine_stopped")

    async def _poll_exchange(self, name: str, adapter: ExchangeAdapter) -> None:
        while self._running:
            try:
                for symbol in list(self._tickers.get(name, {}).keys()) or ["BTC/USDT"]:
                    ticker = await adapter.get_ticker(symbol)
                    self._tickers[name][symbol] = ticker
                    self._last_update[name][symbol] = datetime.now(timezone.utc)

                    order_book = await adapter.get_order_book(symbol)
                    self._order_books[name][symbol] = order_book

                logger.debug("market_data_updated", exchange=name)
            except Exception as e:
                logger.error("market_data_poll_error", exchange=name, error=str(e))

            await asyncio.sleep(1)

    def get_ticker(self, exchange: str, symbol: str) -> Optional[Ticker]:
        return self._tickers.get(exchange, {}).get(symbol)

    def get_order_book(self, exchange: str, symbol: str) -> Optional[OrderBook]:
        return self._order_books.get(exchange, {}).get(symbol)

    def is_stale(self, exchange: str, symbol: str) -> bool:
        last_update = self._last_update.get(exchange, {}).get(symbol)
        if not last_update:
            return True
        age_ms = (datetime.now(timezone.utc) - last_update).total_seconds() * 1000
        return age_ms > self.stale_threshold_ms

    def get_data_age_ms(self, exchange: str, symbol: str) -> Optional[float]:
        last_update = self._last_update.get(exchange, {}).get(symbol)
        if not last_update:
            return None
        return (datetime.now(timezone.utc) - last_update).total_seconds() * 1000

    def get_all_tickers(self, symbol: str) -> dict[str, Ticker]:
        result = {}
        for exchange, tickers in self._tickers.items():
            if symbol in tickers:
                result[exchange] = tickers[symbol]
        return result

    def set_symbols(self, symbols: list[str]) -> None:
        for name in self._exchanges:
            for symbol in symbols:
                if symbol not in self._tickers[name]:
                    self._tickers[name][symbol] = None
                    self._last_update[name][symbol] = datetime.min.replace(tzinfo=timezone.utc)

    def set_ticker(self, exchange: str, symbol: str, ticker: Ticker) -> None:
        if exchange not in self._tickers:
            self._tickers[exchange] = {}
            self._last_update[exchange] = {}
        self._tickers[exchange][symbol] = ticker
        self._last_update[exchange][symbol] = datetime.now(timezone.utc)
