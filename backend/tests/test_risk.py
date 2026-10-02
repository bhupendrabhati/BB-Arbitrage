import pytest
from decimal import Decimal
from app.risk.manager import RiskManager
from app.core.kill_switch import kill_switch


@pytest.mark.asyncio
async def test_risk_manager_approves_valid_trade(risk_manager):
    result = await risk_manager.check_trade(
        trade_amount=Decimal("5"),
        expected_profit=Decimal("0.50"),
        current_capital=Decimal("100"),
    )
    assert result.approved is True


@pytest.mark.asyncio
async def test_risk_manager_rejects_large_trade(risk_manager):
    result = await risk_manager.check_trade(
        trade_amount=Decimal("100"),
        expected_profit=Decimal("10"),
        current_capital=Decimal("200"),
    )
    assert result.approved is False
    assert result.reason == "TRADE_SIZE_LIMIT"


@pytest.mark.asyncio
async def test_risk_manager_rejects_when_kill_switch_active(risk_manager):
    await kill_switch.activate("test")
    result = await risk_manager.check_trade(
        trade_amount=Decimal("5"),
        expected_profit=Decimal("0.50"),
        current_capital=Decimal("100"),
    )
    assert result.approved is False
    assert result.reason == "KILL_SWITCH_ACTIVE"
    await kill_switch.deactivate()


@pytest.mark.asyncio
async def test_risk_manager_rejects_when_capital_insufficient(risk_manager):
    result = await risk_manager.check_trade(
        trade_amount=Decimal("5"),
        expected_profit=Decimal("0.50"),
        current_capital=Decimal("2"),
    )
    assert result.approved is False
    assert result.reason == "CAPITAL_INSUFFICIENT"


def test_risk_manager_records_trades(risk_manager):
    risk_manager.record_trade_open(Decimal("5"))
    assert risk_manager.open_trades == 1
    assert risk_manager.daily_trades == 1

    risk_manager.record_trade_close(Decimal("5"), Decimal("0.50"))
    assert risk_manager.open_trades == 0
    assert risk_manager.daily_pnl == Decimal("0.50")


def test_risk_manager_status(risk_manager):
    status = risk_manager.get_status()
    assert "daily_pnl" in status
    assert "open_trades" in status
    assert "kill_switch_active" in status
