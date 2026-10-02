import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base


class DailyPerformance(Base):
    __tablename__ = "daily_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, nullable=False, unique=True)
    starting_capital = Column(Numeric(20, 8), nullable=False)
    ending_capital = Column(Numeric(20, 8), nullable=False)
    pnl = Column(Numeric(20, 8), default=0)
    pnl_percent = Column(Numeric(10, 6), default=0)
    trades_executed = Column(Numeric(10, 0), default=0)
    winning_trades = Column(Numeric(10, 0), default=0)
    losing_trades = Column(Numeric(10, 0), default=0)
    total_fees = Column(Numeric(20, 8), default=0)
    total_slippage = Column(Numeric(20, 8), default=0)
    opportunities_detected = Column(Numeric(10, 0), default=0)
    opportunities_rejected = Column(Numeric(10, 0), default=0)
    max_drawdown = Column(Numeric(10, 6), default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
