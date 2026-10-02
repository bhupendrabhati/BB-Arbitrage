import pytest
from decimal import Decimal
from app.exchanges.mock import MockExchangeAdapter


@pytest.mark.asyncio
async def test_mock_exchange_get_ticker():
    adapter = MockExchangeAdapter("test")
    ticker = await adapter.get_ticker("BTC/USDT")
    assert ticker.symbol == "BTC/USDT"
    assert ticker.bid > 0
    assert ticker.ask > 0
    assert ticker.ask >= ticker.bid


@pytest.mark.asyncio
async def test_mock_exchange_get_order_book():
    adapter = MockExchangeAdapter("test")
    order_book = await adapter.get_order_book("BTC/USDT")
    assert order_book.symbol == "BTC/USDT"
    assert len(order_book.bids) > 0
    assert len(order_book.asks) > 0


@pytest.mark.asyncio
async def test_mock_exchange_get_balances():
    adapter = MockExchangeAdapter("test")
    balances = await adapter.get_balances()
    assert len(balances) > 0


@pytest.mark.asyncio
async def test_mock_exchange_create_order():
    adapter = MockExchangeAdapter("test")
    result = await adapter.create_order("BTC/USDT", "buy", Decimal("0.001"))
    assert result.status == "filled"
    assert result.filled_quantity == Decimal("0.001")


@pytest.mark.asyncio
async def test_mock_exchange_health_check():
    adapter = MockExchangeAdapter("test")
    healthy = await adapter.health_check()
    assert healthy is True


@pytest.mark.asyncio
async def test_mock_exchange_get_trading_fees():
    adapter = MockExchangeAdapter("test")
    fees = await adapter.get_trading_fees("BTC/USDT")
    assert fees.maker_fee > 0
    assert fees.taker_fee > 0


@pytest.mark.asyncio
async def test_mock_exchange_get_symbol_rules():
    adapter = MockExchangeAdapter("test")
    rules = await adapter.get_symbol_rules("BTC/USDT")
    assert rules.symbol == "BTC/USDT"
    assert rules.base_asset == "BTC"
    assert rules.quote_asset == "USDT"
