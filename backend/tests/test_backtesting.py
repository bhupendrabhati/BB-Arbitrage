import pytest
from decimal import Decimal
from app.backtesting.engine import BacktestingEngine, BacktestConfig


def test_backtesting_engine_basic():
    config = BacktestConfig(
        initial_capital=Decimal("100"),
        max_trade_amount=Decimal("10"),
        min_net_profit=Decimal("0.01"),
    )
    engine = BacktestingEngine(config)

    historical_data = [
        {
            "timestamp": "2024-01-01T12:00:00Z",
            "symbol": "BTC/USDT",
            "buy_exchange": "exchange_a",
            "sell_exchange": "exchange_b",
            "buy_price": "50000",
            "sell_price": "50500",
            "volume": "1",
        },
        {
            "timestamp": "2024-01-01T13:00:00Z",
            "symbol": "BTC/USDT",
            "buy_exchange": "exchange_a",
            "sell_exchange": "exchange_b",
            "buy_price": "50100",
            "sell_price": "50600",
            "volume": "1",
        },
    ]

    result = engine.run_backtest(historical_data)

    assert result.initial_capital == Decimal("100")
    assert result.final_capital > 0
    assert result.total_trades >= 0
    assert result.winning_trades >= 0
    assert result.losing_trades >= 0


def test_backtesting_engine_no_opportunities():
    config = BacktestConfig(min_net_profit=Decimal("1000"))
    engine = BacktestingEngine(config)

    historical_data = [
        {
            "timestamp": "2024-01-01T12:00:00Z",
            "symbol": "BTC/USDT",
            "buy_exchange": "exchange_a",
            "sell_exchange": "exchange_b",
            "buy_price": "50000",
            "sell_price": "50001",
            "volume": "1",
        },
    ]

    result = engine.run_backtest(historical_data)
    assert result.total_trades == 0
    assert result.final_capital == result.initial_capital


def test_backtesting_csv_load():
    engine = BacktestingEngine()
    csv_content = "timestamp,symbol,buy_exchange,sell_exchange,buy_price,sell_price,volume\n2024-01-01T12:00:00Z,BTC/USDT,exchange_a,exchange_b,50000,50500,1\n"
    data = engine.load_csv(csv_content)
    assert len(data) == 1
    assert data[0]["symbol"] == "BTC/USDT"


def test_backtesting_max_drawdown():
    config = BacktestConfig(
        initial_capital=Decimal("100"),
        min_net_profit=Decimal("0.01"),
    )
    engine = BacktestingEngine(config)

    historical_data = [
        {
            "timestamp": f"2024-01-01T{i:02d}:00:00Z",
            "symbol": "BTC/USDT",
            "buy_exchange": "exchange_a",
            "sell_exchange": "exchange_b",
            "buy_price": str(50000 + i * 100),
            "sell_price": str(50500 + i * 100),
            "volume": "1",
        }
        for i in range(10)
    ]

    result = engine.run_backtest(historical_data)
    assert result.max_drawdown >= 0
