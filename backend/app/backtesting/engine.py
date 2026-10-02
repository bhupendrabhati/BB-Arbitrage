import csv
import io
from decimal import Decimal
from datetime import datetime, timezone
from dataclasses import dataclass, field
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("backtesting")


@dataclass
class BacktestConfig:
    initial_capital: Decimal = Decimal("100")
    max_trade_amount: Decimal = Decimal("10")
    min_net_profit: Decimal = Decimal("0.10")
    fee_rate: Decimal = Decimal("0.001")
    slippage_rate: Decimal = Decimal("0.0005")
    max_open_trades: int = 1
    max_trades_per_day: int = 5
    max_daily_loss: Decimal = Decimal("2")


@dataclass
class BacktestTrade:
    timestamp: str
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    quantity: Decimal
    buy_fee: Decimal
    sell_fee: Decimal
    slippage: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    status: str = "completed"


@dataclass
class BacktestResult:
    initial_capital: Decimal
    final_capital: Decimal
    gross_profit: Decimal
    total_fees: Decimal
    total_slippage: Decimal
    net_profit: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: Decimal
    max_drawdown: Decimal
    profit_factor: Decimal
    avg_trade: Decimal
    largest_win: Decimal
    largest_loss: Decimal
    sharpe_ratio: Decimal | None
    trades: list[BacktestTrade] = field(default_factory=list)


class BacktestingEngine:
    def __init__(self, config: BacktestConfig | None = None):
        self.config = config or BacktestConfig()
        self.capital = self.config.initial_capital
        self.peak_capital = self.config.initial_capital
        self.trades: list[BacktestTrade] = []
        self.daily_trades = 0
        self.daily_pnl = Decimal("0")
        self.current_date = ""

    def load_csv(self, csv_content: str) -> list[dict]:
        reader = csv.DictReader(io.StringIO(csv_content))
        data = []
        for row in reader:
            data.append(row)
        return data

    def run_backtest(self, historical_data: list[dict]) -> BacktestResult:
        self.capital = self.config.initial_capital
        self.peak_capital = self.config.initial_capital
        self.trades = []
        self.daily_trades = 0
        self.daily_pnl = Decimal("0")
        self.current_date = ""

        for row in historical_data:
            timestamp = row.get("timestamp", "")
            symbol = row.get("symbol", "BTC/USDT")
            buy_exchange = row.get("buy_exchange", "exchange_a")
            sell_exchange = row.get("sell_exchange", "exchange_b")
            buy_price = Decimal(str(row.get("buy_price", "0")))
            sell_price = Decimal(str(row.get("sell_price", "0")))

            trade_date = timestamp[:10] if timestamp else ""
            if trade_date != self.current_date:
                self.current_date = trade_date
                self.daily_trades = 0
                self.daily_pnl = Decimal("0")

            if self.daily_pnl < -self.config.max_daily_loss:
                continue
            if self.daily_trades >= self.config.max_trades_per_day:
                continue

            if sell_price <= buy_price:
                continue

            quantity = min(
                self.config.max_trade_amount / buy_price,
                Decimal(str(row.get("volume", "1"))),
            )

            buy_fee = buy_price * quantity * self.config.fee_rate
            sell_fee = sell_price * quantity * self.config.fee_rate
            slippage = buy_price * quantity * self.config.slippage_rate

            total_cost = buy_fee + sell_fee + slippage
            gross_profit = (sell_price - buy_price) * quantity
            net_profit = gross_profit - total_cost

            if net_profit < self.config.min_net_profit:
                continue

            if total_cost > self.capital:
                continue

            self.capital += net_profit
            self.daily_pnl += net_profit
            self.daily_trades += 1

            if self.capital > self.peak_capital:
                self.peak_capital = self.capital

            trade = BacktestTrade(
                timestamp=timestamp,
                symbol=symbol,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                buy_price=buy_price,
                sell_price=sell_price,
                quantity=quantity,
                buy_fee=buy_fee,
                sell_fee=sell_fee,
                slippage=slippage,
                gross_profit=gross_profit,
                net_profit=net_profit,
            )
            self.trades.append(trade)

        return self._calculate_results()

    def _calculate_results(self) -> BacktestResult:
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.net_profit > 0)
        losing_trades = total_trades - winning_trades

        gross_profit = sum(t.gross_profit for t in self.trades)
        total_fees = sum(t.buy_fee + t.sell_fee for t in self.trades)
        total_slippage = sum(t.slippage for t in self.trades)
        net_profit = sum(t.net_profit for t in self.trades)

        win_rate = (Decimal(str(winning_trades)) / Decimal(str(total_trades)) * 100) if total_trades > 0 else Decimal("0")
        avg_trade = (net_profit / Decimal(str(total_trades))) if total_trades > 0 else Decimal("0")

        wins = [t.net_profit for t in self.trades if t.net_profit > 0]
        losses = [t.net_profit for t in self.trades if t.net_profit <= 0]

        largest_win = max(wins) if wins else Decimal("0")
        largest_loss = min(losses) if losses else Decimal("0")

        total_wins = sum(wins) if wins else Decimal("0")
        total_losses = abs(sum(losses)) if losses else Decimal("0")
        profit_factor = (total_wins / total_losses) if total_losses > 0 else Decimal("0")

        max_drawdown = self._calculate_max_drawdown()
        sharpe_ratio = self._calculate_sharpe_ratio()

        return BacktestResult(
            initial_capital=self.config.initial_capital,
            final_capital=self.capital,
            gross_profit=gross_profit,
            total_fees=total_fees,
            total_slippage=total_slippage,
            net_profit=net_profit,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            profit_factor=profit_factor,
            avg_trade=avg_trade,
            largest_win=largest_win,
            largest_loss=largest_loss,
            sharpe_ratio=sharpe_ratio,
            trades=self.trades,
        )

    def _calculate_max_drawdown(self) -> Decimal:
        if not self.trades:
            return Decimal("0")

        peak = self.config.initial_capital
        max_dd = Decimal("0")
        current = self.config.initial_capital

        for trade in self.trades:
            current += trade.net_profit
            if current > peak:
                peak = current
            dd = (peak - current) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_sharpe_ratio(self) -> Decimal | None:
        if len(self.trades) < 2:
            return None

        returns = [t.net_profit for t in self.trades]
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** Decimal("0.5")

        if std_dev == 0:
            return None

        risk_free_rate = Decimal("0.05") / 365
        sharpe = (mean_return - risk_free_rate) / std_dev * (365 ** Decimal("0.5"))
        return sharpe.quantize(Decimal("0.0001"))
