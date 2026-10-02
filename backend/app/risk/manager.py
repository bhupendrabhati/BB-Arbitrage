from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timezone, date
from typing import Optional
from app.core.kill_switch import kill_switch
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("risk")


@dataclass
class RiskCheckResult:
    approved: bool
    reason: Optional[str] = None
    details: Optional[str] = None


class RiskManager:
    def __init__(self):
        self.daily_pnl = Decimal("0")
        self.daily_trades = 0
        self.open_trades = 0
        self.total_exposure = Decimal("0")
        self.current_date: Optional[date] = None
        self._trade_history: list[dict] = []

    def _reset_daily(self) -> None:
        today = date.today()
        if self.current_date != today:
            self.daily_pnl = Decimal("0")
            self.daily_trades = 0
            self.current_date = today

    async def check_trade(
        self,
        trade_amount: Decimal,
        expected_profit: Decimal,
        current_capital: Decimal,
    ) -> RiskCheckResult:
        self._reset_daily()

        if kill_switch.is_active:
            logger.warning("risk_check_kill_switch_active")
            return RiskCheckResult(
                approved=False,
                reason="KILL_SWITCH_ACTIVE",
                details="Kill switch is activated",
            )

        if settings.TRADING_MODE.value == "scanner":
            return RiskCheckResult(approved=True)

        if trade_amount > settings.MAX_TRADE_AMOUNT_INR:
            logger.warning("risk_check_trade_too_large", amount=trade_amount, limit=settings.MAX_TRADE_AMOUNT_INR)
            return RiskCheckResult(
                approved=False,
                reason="TRADE_SIZE_LIMIT",
                details=f"Trade amount {trade_amount} exceeds maximum {settings.MAX_TRADE_AMOUNT_INR}",
            )

        if self.daily_pnl < -settings.MAX_DAILY_LOSS_INR:
            logger.warning("risk_check_daily_loss_limit", daily_pnl=self.daily_pnl, limit=-settings.MAX_DAILY_LOSS_INR)
            return RiskCheckResult(
                approved=False,
                reason="DAILY_LOSS_LIMIT",
                details=f"Daily loss {self.daily_pnl} exceeds maximum {settings.MAX_DAILY_LOSS_INR}",
            )

        if self.open_trades >= settings.MAX_OPEN_TRADES:
            logger.warning("risk_check_max_open_trades", open=self.open_trades, limit=settings.MAX_OPEN_TRADES)
            return RiskCheckResult(
                approved=False,
                reason="MAX_OPEN_TRADES",
                details=f"Open trades {self.open_trades} reaches maximum {settings.MAX_OPEN_TRADES}",
            )

        if self.daily_trades >= settings.MAX_TRADES_PER_DAY:
            logger.warning("risk_check_max_trades_per_day", trades=self.daily_trades, limit=settings.MAX_TRADES_PER_DAY)
            return RiskCheckResult(
                approved=False,
                reason="MAX_TRADES_PER_DAY",
                details=f"Daily trades {self.daily_trades} reaches maximum {settings.MAX_TRADES_PER_DAY}",
            )

        if trade_amount > current_capital:
            logger.warning("risk_check_capital_insufficient", amount=trade_amount, capital=current_capital)
            return RiskCheckResult(
                approved=False,
                reason="CAPITAL_INSUFFICIENT",
                details=f"Trade amount {trade_amount} exceeds available capital {current_capital}",
            )

        logger.info("risk_check_approved", amount=trade_amount, expected_profit=expected_profit)
        return RiskCheckResult(approved=True)

    def record_trade_open(self, trade_amount: Decimal) -> None:
        self._reset_daily()
        self.open_trades += 1
        self.daily_trades += 1
        self.total_exposure += trade_amount

    def record_trade_close(self, trade_amount: Decimal, pnl: Decimal) -> None:
        self._reset_daily()
        self.open_trades = max(0, self.open_trades - 1)
        self.total_exposure = max(Decimal("0"), self.total_exposure - trade_amount)
        self.daily_pnl += pnl

    def get_status(self) -> dict:
        self._reset_daily()
        return {
            "daily_pnl": str(self.daily_pnl),
            "daily_trades": self.daily_trades,
            "open_trades": self.open_trades,
            "total_exposure": str(self.total_exposure),
            "daily_loss_limit": str(-settings.MAX_DAILY_LOSS_INR),
            "max_open_trades": settings.MAX_OPEN_TRADES,
            "max_trades_per_day": settings.MAX_TRADES_PER_DAY,
            "kill_switch_active": kill_switch.is_active,
        }


risk_manager = RiskManager()
