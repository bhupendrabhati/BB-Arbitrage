from decimal import Decimal
from datetime import datetime, timezone
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("portfolio")


class PortfolioTracker:
    def __init__(self):
        self.initial_capital = Decimal(str(settings.INITIAL_CAPITAL_INR))
        self.current_capital = Decimal(str(settings.INITIAL_CAPITAL_INR))
        self.total_pnl = Decimal("0")
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = Decimal("0")
        self.peak_capital = Decimal(str(settings.INITIAL_CAPITAL_INR))
        self.daily_pnl: dict[str, Decimal] = {}
        self.trade_history: list[dict] = []

    def record_trade(
        self,
        trade_id: str,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_price: Decimal,
        sell_price: Decimal,
        quantity: Decimal,
        fees: Decimal,
        net_profit: Decimal,
        mode: str,
    ) -> None:
        self.total_trades += 1
        self.current_capital += net_profit
        self.total_pnl += net_profit

        if net_profit > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital

        drawdown = (self.peak_capital - self.current_capital) / self.peak_capital * 100
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

        today = datetime.now(timezone.utc).date().isoformat()
        if today not in self.daily_pnl:
            self.daily_pnl[today] = Decimal("0")
        self.daily_pnl[today] += net_profit

        trade_record = {
            "id": trade_id,
            "symbol": symbol,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "buy_price": str(buy_price),
            "sell_price": str(sell_price),
            "quantity": str(quantity),
            "fees": str(fees),
            "net_profit": str(net_profit),
            "mode": mode,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.trade_history.append(trade_record)

        logger.info(
            "portfolio_trade_recorded",
            trade_id=trade_id,
            net_profit=str(net_profit),
            capital=str(self.current_capital),
        )

    def get_summary(self) -> dict:
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else Decimal("0")
        today = datetime.now(timezone.utc).date().isoformat()
        return {
            "initial_capital": str(self.initial_capital),
            "current_capital": str(self.current_capital),
            "total_pnl": str(self.total_pnl),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": str(win_rate),
            "max_drawdown": str(self.max_drawdown),
            "today_pnl": str(self.daily_pnl.get(today, Decimal("0"))),
        }

    def get_trade_history(self, limit: int = 100) -> list[dict]:
        return self.trade_history[-limit:]


portfolio_tracker = PortfolioTracker()
