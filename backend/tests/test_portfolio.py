import pytest
from decimal import Decimal
from app.portfolio.tracker import PortfolioTracker


def test_portfolio_tracker_record_trade():
    tracker = PortfolioTracker()
    tracker.record_trade(
        trade_id="test-123",
        symbol="BTC/USDT",
        buy_exchange="exchange_a",
        sell_exchange="exchange_b",
        buy_price=Decimal("50000"),
        sell_price=Decimal("50500"),
        quantity=Decimal("0.001"),
        fees=Decimal("0.10"),
        net_profit=Decimal("0.40"),
        mode="paper",
    )

    assert tracker.total_trades == 1
    assert tracker.winning_trades == 1
    assert tracker.total_pnl == Decimal("0.40")
    assert tracker.current_capital == Decimal("100.40")


def test_portfolio_tracker_losing_trade():
    tracker = PortfolioTracker()
    tracker.record_trade(
        trade_id="test-456",
        symbol="BTC/USDT",
        buy_exchange="exchange_a",
        sell_exchange="exchange_b",
        buy_price=Decimal("50000"),
        sell_price=Decimal("49900"),
        quantity=Decimal("0.001"),
        fees=Decimal("0.10"),
        net_profit=Decimal("-0.20"),
        mode="paper",
    )

    assert tracker.total_trades == 1
    assert tracker.losing_trades == 1
    assert tracker.total_pnl == Decimal("-0.20")


def test_portfolio_tracker_summary():
    tracker = PortfolioTracker()
    summary = tracker.get_summary()
    assert "initial_capital" in summary
    assert "current_capital" in summary
    assert "total_pnl" in summary
    assert "win_rate" in summary
    assert "max_drawdown" in summary


def test_portfolio_tracker_trade_history():
    tracker = PortfolioTracker()
    tracker.record_trade(
        trade_id="test-789",
        symbol="ETH/USDT",
        buy_exchange="exchange_a",
        sell_exchange="exchange_b",
        buy_price=Decimal("3000"),
        sell_price=Decimal("3050"),
        quantity=Decimal("0.1"),
        fees=Decimal("0.60"),
        net_profit=Decimal("4.40"),
        mode="paper",
    )

    history = tracker.get_trade_history()
    assert len(history) == 1
    assert history[0]["id"] == "test-789"
