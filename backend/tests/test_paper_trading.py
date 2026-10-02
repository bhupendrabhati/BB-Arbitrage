import pytest
from decimal import Decimal
from app.paper_trading.engine import PaperTradingEngine


@pytest.mark.asyncio
async def test_paper_trade_execution():
    engine = PaperTradingEngine()
    initial_capital = engine.capital

    result = await engine.execute_trade(
        symbol="BTC/USDT",
        buy_exchange="exchange_a",
        sell_exchange="exchange_b",
        buy_price=Decimal("50000"),
        sell_price=Decimal("50500"),
        quantity=Decimal("0.001"),
        buy_fee=Decimal("0.05"),
        sell_fee=Decimal("0.05"),
        slippage=Decimal("5"),
    )

    assert result["success"] is True
    assert "trade_id" in result
    assert engine.capital != initial_capital or len(engine.trades) > 0


def test_paper_trading_status():
    engine = PaperTradingEngine()
    status = engine.get_status()
    assert "capital" in status
    assert "total_pnl" in status
    assert "total_trades" in status
    assert "win_rate" in status


def test_paper_trading_get_trades():
    engine = PaperTradingEngine()
    trades = engine.get_trades()
    assert isinstance(trades, list)


@pytest.mark.asyncio
async def test_paper_trade_insufficient_capital():
    engine = PaperTradingEngine()
    engine.capital = Decimal("0.01")

    result = await engine.execute_trade(
        symbol="BTC/USDT",
        buy_exchange="exchange_a",
        sell_exchange="exchange_b",
        buy_price=Decimal("50000"),
        sell_price=Decimal("50500"),
        quantity=Decimal("0.001"),
        buy_fee=Decimal("0.05"),
        sell_fee=Decimal("0.05"),
        slippage=Decimal("5"),
    )

    assert result["success"] is False
