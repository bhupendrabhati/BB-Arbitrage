import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.user import Base
import enum


class TradeStatus(str, enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REJECTED = "rejected"


class OrderSide(str, enum.Enum):
    BUY = "buy"
    SELL = "sell"


class TradeMode(str, enum.Enum):
    SCANNER = "scanner"
    PAPER = "paper"
    LIVE = "live"


class Trade(Base):
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("arbitrage_opportunities.id"), nullable=True)
    symbol = Column(String(20), nullable=False)
    mode = Column(SAEnum(TradeMode), nullable=False)
    buy_exchange = Column(String(100), nullable=False)
    sell_exchange = Column(String(100), nullable=False)
    buy_price = Column(Numeric(20, 8), nullable=False)
    sell_price = Column(Numeric(20, 8), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    buy_fee = Column(Numeric(20, 8), default=0)
    sell_fee = Column(Numeric(20, 8), default=0)
    slippage = Column(Numeric(20, 8), default=0)
    network_cost = Column(Numeric(20, 8), default=0)
    gross_profit = Column(Numeric(20, 8), nullable=False)
    net_profit = Column(Numeric(20, 8), nullable=False)
    status = Column(SAEnum(TradeStatus), default=TradeStatus.PENDING)
    buy_order_id = Column(String(100), nullable=True)
    sell_order_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    executed_at = Column(DateTime(timezone=True), nullable=True)
    settled_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="trades")
    orders = relationship("Order", back_populates="trade")


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(UUID(as_uuid=True), ForeignKey("trades.id"), nullable=False)
    exchange = Column(String(100), nullable=False)
    exchange_order_id = Column(String(100), nullable=True)
    symbol = Column(String(20), nullable=False)
    side = Column(SAEnum(OrderSide), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)
    quantity = Column(Numeric(20, 8), nullable=False)
    filled_quantity = Column(Numeric(20, 8), default=0)
    fee = Column(Numeric(20, 8), default=0)
    status = Column(SAEnum(TradeStatus), default=TradeStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    trade = relationship("Trade", back_populates="orders")
