import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base
import enum


class BacktestStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    status = Column(SAEnum(BacktestStatus), default=BacktestStatus.PENDING)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Numeric(20, 8), nullable=False)
    final_capital = Column(Numeric(20, 8), nullable=True)
    gross_profit = Column(Numeric(20, 8), default=0)
    total_fees = Column(Numeric(20, 8), default=0)
    total_slippage = Column(Numeric(20, 8), default=0)
    net_profit = Column(Numeric(20, 8), default=0)
    total_trades = Column(Numeric(10, 0), default=0)
    winning_trades = Column(Numeric(10, 0), default=0)
    losing_trades = Column(Numeric(10, 0), default=0)
    win_rate = Column(Numeric(5, 2), default=0)
    max_drawdown = Column(Numeric(10, 6), default=0)
    profit_factor = Column(Numeric(10, 4), default=0)
    avg_trade = Column(Numeric(20, 8), default=0)
    largest_win = Column(Numeric(20, 8), default=0)
    largest_loss = Column(Numeric(20, 8), default=0)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    config_json = Column(Text, default="{}")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)


class BacktestTrade(Base):
    __tablename__ = "backtest_trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    backtest_run_id = Column(UUID(as_uuid=True), ForeignKey("backtest_runs.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    buy_exchange = Column(String(100), nullable=False)
    sell_exchange = Column(String(100), nullable=False)
    buy_price = Column(Numeric(20, 8), nullable=False)
    sell_price = Column(Numeric(20, 8), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    buy_fee = Column(Numeric(20, 8), default=0)
    sell_fee = Column(Numeric(20, 8), default=0)
    slippage = Column(Numeric(20, 8), default=0)
    gross_profit = Column(Numeric(20, 8), nullable=False)
    net_profit = Column(Numeric(20, 8), nullable=False)
    status = Column(String(20), default="completed")
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
