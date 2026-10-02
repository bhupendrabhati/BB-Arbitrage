import pytest
from decimal import Decimal
from datetime import datetime, timezone
from app.exchanges.base import Ticker, OrderBook, OrderBookLevel
from app.market_data.engine import MarketDataEngine
from app.arbitrage.engine import ArbitrageEngine
from app.exchanges.mock import MockExchangeAdapter


@pytest.mark.asyncio
async def test_no_opportunity_when_prices_equal(market_data_engine, arbitrage_engine):
    adapter_a = MockExchangeAdapter("exchange_a")
    adapter_b = MockExchangeAdapter("exchange_b")

    market_data_engine.register_exchange("exchange_a", adapter_a)
    market_data_engine.register_exchange("exchange_b", adapter_b)

    ticker = Ticker(
        symbol="BTC/USDT",
        bid=Decimal("50000"),
        ask=Decimal("50000"),
        bid_quantity=Decimal("1"),
        ask_quantity=Decimal("1"),
    )
    market_data_engine.set_ticker("exchange_a", "BTC/USDT", ticker)
    market_data_engine.set_ticker("exchange_b", "BTC/USDT", ticker)

    opportunities = arbitrage_engine.scan_pair("BTC/USDT")
    assert len(opportunities) == 0 or all(not o.is_executable for o in opportunities)


@pytest.mark.asyncio
async def test_opportunity_detected_with_spread(market_data_engine, arbitrage_engine):
    adapter_a = MockExchangeAdapter("exchange_a")
    adapter_b = MockExchangeAdapter("exchange_b")

    market_data_engine.register_exchange("exchange_a", adapter_a)
    market_data_engine.register_exchange("exchange_b", adapter_b)

    ticker_a = Ticker(
        symbol="BTC/USDT",
        bid=Decimal("49900"),
        ask=Decimal("50000"),
        bid_quantity=Decimal("10"),
        ask_quantity=Decimal("10"),
    )
    ticker_b = Ticker(
        symbol="BTC/USDT",
        bid=Decimal("50500"),
        ask=Decimal("50600"),
        bid_quantity=Decimal("10"),
        ask_quantity=Decimal("10"),
    )
    market_data_engine.set_ticker("exchange_a", "BTC/USDT", ticker_a)
    market_data_engine.set_ticker("exchange_b", "BTC/USDT", ticker_b)

    opportunities = arbitrage_engine.scan_pair("BTC/USDT")
    assert len(opportunities) > 0

    opp = opportunities[0]
    assert opp.sell_price > opp.buy_price
    assert opp.gross_spread > 0


def test_slippage_estimation(arbitrage_engine):
    ticker = Ticker(
        symbol="BTC/USDT",
        bid=Decimal("50000"),
        ask=Decimal("50000"),
        bid_quantity=Decimal("1"),
        ask_quantity=Decimal("1"),
    )
    slippage = arbitrage_engine._estimate_slippage(ticker, Decimal("0.5"))
    assert slippage >= 0
    assert slippage <= arbitrage_engine._max_slippage


def test_fee_calculation(arbitrage_engine):
    fee = arbitrage_engine._get_fee("test_exchange")
    assert fee == Decimal("0.001")

    arbitrage_engine.set_fee("custom_exchange", Decimal("0.002"), Decimal("0.003"))
    fee = arbitrage_engine._get_fee("custom_exchange")
    assert fee == Decimal("0.003")
