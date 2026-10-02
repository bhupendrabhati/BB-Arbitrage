from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime
from typing import Optional


@dataclass
class Ticker:
    symbol: str
    bid: Decimal
    ask: Decimal
    bid_quantity: Decimal
    ask_quantity: Decimal
    last_price: Optional[Decimal] = None
    timestamp: Optional[datetime] = None


@dataclass
class OrderBookLevel:
    price: Decimal
    quantity: Decimal


@dataclass
class OrderBook:
    symbol: str
    bids: list[OrderBookLevel]
    asks: list[OrderBookLevel]
    timestamp: Optional[datetime] = None


@dataclass
class Balance:
    asset: str
    free: Decimal
    locked: Decimal


@dataclass
class OrderResult:
    order_id: str
    status: str
    filled_quantity: Decimal
    average_price: Decimal
    fee: Decimal
    fee_asset: str


@dataclass
class TradingFees:
    maker_fee: Decimal
    taker_fee: Decimal


@dataclass
class SymbolRules:
    symbol: str
    base_asset: str
    quote_asset: str
    min_order_size: Decimal
    max_order_size: Decimal
    tick_size: Decimal
    lot_size: Decimal


class ExchangeAdapter(ABC):
    """Abstract base class for exchange adapters."""

    def __init__(self, name: str, api_key: str = "", api_secret: str = ""):
        self.name = name
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Ticker:
        pass

    @abstractmethod
    async def get_order_book(self, symbol: str, limit: int = 20) -> OrderBook:
        pass

    @abstractmethod
    async def get_balances(self) -> list[Balance]:
        pass

    @abstractmethod
    async def create_order(
        self, symbol: str, side: str, quantity: Decimal, price: Optional[Decimal] = None
    ) -> OrderResult:
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str, symbol: str) -> OrderResult:
        pass

    @abstractmethod
    async def get_trading_fees(self, symbol: str) -> TradingFees:
        pass

    @abstractmethod
    async def get_symbol_rules(self, symbol: str) -> SymbolRules:
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        pass
