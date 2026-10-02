import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base
import enum


class OpportunityStatus(str, enum.Enum):
    DETECTED = "detected"
    EXECUTABLE = "executable"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"


class RejectionReason(str, enum.Enum):
    INSUFFICIENT_LIQUIDITY = "INSUFFICIENT_LIQUIDITY"
    STALE_MARKET_DATA = "STALE_MARKET_DATA"
    SPREAD_TOO_SMALL = "SPREAD_TOO_SMALL"
    FEES_TOO_HIGH = "FEES_TOO_HIGH"
    SLIPPAGE_TOO_HIGH = "SLIPPAGE_TOO_HIGH"
    MIN_ORDER_NOT_MET = "MIN_ORDER_NOT_MET"
    RISK_LIMIT_REACHED = "RISK_LIMIT_REACHED"
    DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"
    EXCHANGE_UNAVAILABLE = "EXCHANGE_UNAVAILABLE"
    ORDER_BOOK_CHANGED = "ORDER_BOOK_CHANGED"
    CAPITAL_INSUFFICIENT = "CAPITAL_INSUFFICIENT"
    UNKNOWN_ORDER_STATE = "UNKNOWN_ORDER_STATE"
    NET_PROFIT_BELOW_THRESHOLD = "NET_PROFIT_BELOW_THRESHOLD"
    KILL_SWITCH_ACTIVE = "KILL_SWITCH_ACTIVE"


class ArbitrageOpportunity(Base):
    __tablename__ = "arbitrage_opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buy_exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False)
    sell_exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    buy_price = Column(Numeric(20, 8), nullable=False)
    sell_price = Column(Numeric(20, 8), nullable=False)
    gross_spread = Column(Numeric(20, 8), nullable=False)
    gross_spread_percent = Column(Numeric(10, 6), nullable=False)
    buy_fee = Column(Numeric(20, 8), nullable=False)
    sell_fee = Column(Numeric(20, 8), nullable=False)
    estimated_slippage = Column(Numeric(20, 8), nullable=False)
    network_cost = Column(Numeric(20, 8), default=0)
    other_costs = Column(Numeric(20, 8), default=0)
    total_cost = Column(Numeric(20, 8), nullable=False)
    gross_profit = Column(Numeric(20, 8), nullable=False)
    net_profit = Column(Numeric(20, 8), nullable=False)
    net_profit_percent = Column(Numeric(10, 6), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    status = Column(SAEnum(OpportunityStatus), default=OpportunityStatus.DETECTED)
    rejection_reason = Column(SAEnum(RejectionReason), nullable=True)
    rejection_details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    evaluated_at = Column(DateTime(timezone=True), nullable=True)
    trade_id = Column(UUID(as_uuid=True), ForeignKey("trades.id"), nullable=True)
