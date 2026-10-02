import uuid
from decimal import Decimal
from datetime import datetime, timezone
from dataclasses import dataclass, field
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("paper_trading")


@dataclass
class PaperOrder:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    symbol: str = ""
    side: str = ""
    quantity: Decimal = Decimal("0")
    price: Decimal = Decimal("0")
    status: str = "pending"
    filled_quantity: Decimal = Decimal("0")
    average_price: Decimal = Decimal("0")
    fee: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    filled_at: datetime | None = None
    error: str | None = None


class PaperTradingEngine:
    def __init__(self):
        self.capital = Decimal(str(settings.INITIAL_CAPITAL_INR))
        self.initial_capital = Decimal(str(settings.INITIAL_CAPITAL_INR))
        self.orders: list[PaperOrder] = []
        self.trades: list[dict] = []
        self.total_fees = Decimal("0")
        self.total_slippage = Decimal("0")
        self.total_pnl = Decimal("0")
        self.winning_trades = 0
        self.losing_trades = 0

    async def execute_trade(
        self,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_price: Decimal,
        sell_price: Decimal,
        quantity: Decimal,
        buy_fee: Decimal,
        sell_fee: Decimal,
        slippage: Decimal,
    ) -> dict:
        simulated_latency = 0.05
        simulated_partial_fill = False
        simulated_rejection = False

        import random
        if random.random() < 0.02:
            simulated_rejection = True
        if random.random() < 0.05:
            simulated_partial_fill = True
            quantity = quantity * Decimal(str(random.uniform(0.5, 0.95)))

        if simulated_rejection:
            order = PaperOrder(
                symbol=symbol,
                side="buy",
                quantity=quantity,
                price=buy_price,
                status="rejected",
                error="Simulated exchange rejection",
            )
            self.orders.append(order)
            logger.warning("paper_trade_rejected", symbol=symbol, exchange=buy_exchange)
            return {"success": False, "error": "Simulated rejection", "order_id": order.id}

        actual_buy_price = buy_price * (1 + slippage / buy_price)
        actual_sell_price = sell_price * (1 - slippage / sell_price)

        total_cost = (actual_buy_price * quantity) + buy_fee + sell_fee
        if total_cost > self.capital:
            logger.warning("paper_trade_insufficient_capital", required=total_cost, available=self.capital)
            return {"success": False, "error": "Insufficient capital"}

        self.capital -= total_cost

        gross_profit = (actual_sell_price - actual_buy_price) * quantity
        net_profit = gross_profit - buy_fee - sell_fee

        self.capital += actual_sell_price * quantity
        self.total_pnl += net_profit
        self.total_fees += buy_fee + sell_fee
        self.total_slippage += slippage * quantity

        if net_profit > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        trade_record = {
            "id": str(uuid.uuid4()),
            "symbol": symbol,
            "buy_exchange": buy_exchange,
            "sell_exchange": sell_exchange,
            "buy_price": str(actual_buy_price),
            "sell_price": str(actual_sell_price),
            "quantity": str(quantity),
            "buy_fee": str(buy_fee),
            "sell_fee": str(sell_fee),
            "slippage": str(slippage * quantity),
            "gross_profit": str(gross_profit),
            "net_profit": str(net_profit),
            "status": "completed",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.trades.append(trade_record)

        buy_order = PaperOrder(
            symbol=symbol,
            side="buy",
            quantity=quantity,
            price=actual_buy_price,
            status="filled",
            filled_quantity=quantity,
            average_price=actual_buy_price,
            fee=buy_fee,
            filled_at=datetime.now(timezone.utc),
        )
        sell_order = PaperOrder(
            symbol=symbol,
            side="sell",
            quantity=quantity,
            price=actual_sell_price,
            status="filled",
            filled_quantity=quantity,
            average_price=actual_sell_price,
            fee=sell_fee,
            filled_at=datetime.now(timezone.utc),
        )
        self.orders.extend([buy_order, sell_order])

        logger.info(
            "paper_trade_executed",
            symbol=symbol,
            net_profit=str(net_profit),
            capital=str(self.capital),
        )

        return {
            "success": True,
            "trade_id": trade_record["id"],
            "buy_order_id": buy_order.id,
            "sell_order_id": sell_order.id,
            "net_profit": str(net_profit),
            "capital": str(self.capital),
        }

    def get_status(self) -> dict:
        total_trades = self.winning_trades + self.losing_trades
        win_rate = (self.winning_trades / total_trades * 100) if total_trades > 0 else Decimal("0")
        return {
            "capital": str(self.capital),
            "initial_capital": str(self.initial_capital),
            "total_pnl": str(self.total_pnl),
            "total_fees": str(self.total_fees),
            "total_slippage": str(self.total_slippage),
            "total_trades": total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": str(win_rate),
        }

    def get_trades(self, limit: int = 100) -> list[dict]:
        return self.trades[-limit:]


paper_trading_engine = PaperTradingEngine()
