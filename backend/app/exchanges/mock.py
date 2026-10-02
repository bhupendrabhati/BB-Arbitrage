import uuid
from decimal import Decimal
from datetime import datetime, timezone
import random
from app.exchanges.base import (
    ExchangeAdapter, Ticker, OrderBook, OrderBookLevel,
    Balance, OrderResult, TradingFees, SymbolRules,
)


class MockExchangeAdapter(ExchangeAdapter):
    """Mock exchange adapter for testing and paper trading."""

    def __init__(self, name: str = "mock"):
        super().__init__(name=name)
        self._tickers: dict[str, Ticker] = {}
        self._order_books: dict[str, OrderBook] = {}
        self._balances: dict[str, Balance] = {
            "INR": Balance(asset="INR", free=Decimal("100"), locked=Decimal("0")),
            "USDT": Balance(asset="USDT", free=Decimal("0"), locked=Decimal("0")),
            "BTC": Balance(asset="BTC", free=Decimal("0"), locked=Decimal("0")),
            "ETH": Balance(asset="ETH", free=Decimal("0"), locked=Decimal("0")),
        }
        self._orders: dict[str, OrderResult] = {}
        self._fail_next_order = False
        self._latency_ms = 50

    def set_ticker(self, symbol: str, ticker: Ticker) -> None:
        self._tickers[symbol] = ticker

    def set_order_book(self, symbol: str, order_book: OrderBook) -> None:
        self._order_books[symbol] = order_book

    def set_fail_next_order(self, fail: bool) -> None:
        self._fail_next_order = fail

    async def get_ticker(self, symbol: str) -> Ticker:
        if symbol in self._tickers:
            return self._tickers[symbol]
        base_price = Decimal("50000") if "BTC" in symbol else Decimal("3000")
        spread = base_price * Decimal("0.001")
        return Ticker(
            symbol=symbol,
            bid=base_price - spread / 2,
            ask=base_price + spread / 2,
            bid_quantity=Decimal("1.0"),
            ask_quantity=Decimal("1.0"),
            last_price=base_price,
            timestamp=datetime.now(timezone.utc),
        )

    async def get_order_book(self, symbol: str, limit: int = 20) -> OrderBook:
        if symbol in self._order_books:
            return self._order_books[symbol]
        ticker = await self.get_ticker(symbol)
        bids = [
            OrderBookLevel(price=ticker.bid - Decimal(str(i * 0.01)), quantity=Decimal(str(random.uniform(0.1, 5.0))))
            for i in range(limit)
        ]
        asks = [
            OrderBookLevel(price=ticker.ask + Decimal(str(i * 0.01)), quantity=Decimal(str(random.uniform(0.1, 5.0))))
            for i in range(limit)
        ]
        return OrderBook(symbol=symbol, bids=bids, asks=asks, timestamp=datetime.now(timezone.utc))

    async def get_balances(self) -> list[Balance]:
        return list(self._balances.values())

    async def create_order(
        self, symbol: str, side: str, quantity: Decimal, price: Decimal | None = None
    ) -> OrderResult:
        if self._fail_next_order:
            self._fail_next_order = False
            raise Exception("Mock exchange order failure")

        order_id = str(uuid.uuid4())
        fill_price = price or Decimal("50000")
        fee = fill_price * quantity * Decimal("0.001")

        result = OrderResult(
            order_id=order_id,
            status="filled",
            filled_quantity=quantity,
            average_price=fill_price,
            fee=fee,
            fee_asset=symbol.split("/")[0] if "/" in symbol else "USDT",
        )
        self._orders[order_id] = result

        asset = symbol.split("/")[0] if "/" in symbol else "USDT"
        if side == "buy" and asset in self._balances:
            self._balances[asset] = Balance(
                asset=asset,
                free=self._balances[asset].free + quantity,
                locked=self._balances[asset].locked,
            )
        elif side == "sell" and asset in self._balances:
            self._balances[asset] = Balance(
                asset=asset,
                free=max(Decimal("0"), self._balances[asset].free - quantity),
                locked=self._balances[asset].locked,
            )

        return result

    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        if order_id in self._orders:
            self._orders[order_id] = OrderResult(
                order_id=order_id,
                status="cancelled",
                filled_quantity=Decimal("0"),
                average_price=Decimal("0"),
                fee=Decimal("0"),
                fee_asset="",
            )
            return True
        return False

    async def get_order_status(self, order_id: str, symbol: str) -> OrderResult:
        if order_id in self._orders:
            return self._orders[order_id]
        return OrderResult(
            order_id=order_id,
            status="unknown",
            filled_quantity=Decimal("0"),
            average_price=Decimal("0"),
            fee=Decimal("0"),
            fee_asset="",
        )

    async def get_trading_fees(self, symbol: str) -> TradingFees:
        return TradingFees(maker_fee=Decimal("0.001"), taker_fee=Decimal("0.001"))

    async def get_symbol_rules(self, symbol: str) -> SymbolRules:
        base = symbol.split("/")[0] if "/" in symbol else "BTC"
        quote = symbol.split("/")[1] if "/" in symbol else "USDT"
        return SymbolRules(
            symbol=symbol,
            base_asset=base,
            quote_asset=quote,
            min_order_size=Decimal("0.001"),
            max_order_size=Decimal("1000"),
            tick_size=Decimal("0.01"),
            lot_size=Decimal("0.001"),
        )

    async def health_check(self) -> bool:
        return True
