import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from app.models.user import Base


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    bid = Column(Numeric(20, 8), nullable=False)
    ask = Column(Numeric(20, 8), nullable=False)
    bid_quantity = Column(Numeric(20, 8), nullable=False)
    ask_quantity = Column(Numeric(20, 8), nullable=False)
    last_price = Column(Numeric(20, 8), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    sequence_number = Column(BigInteger, nullable=True)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class OrderBookSnapshot(Base):
    __tablename__ = "order_book_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exchange_id = Column(UUID(as_uuid=True), ForeignKey("exchanges.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    bids_json = Column(String(10000), nullable=False)
    asks_json = Column(String(10000), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
