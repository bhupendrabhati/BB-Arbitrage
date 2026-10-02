import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.user import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False, default="Main")
    initial_capital = Column(Numeric(20, 8), nullable=False, default=100)
    current_capital = Column(Numeric(20, 8), nullable=False, default=100)
    total_pnl = Column(Numeric(20, 8), default=0)
    total_trades = Column(Numeric(10, 0), default=0)
    winning_trades = Column(Numeric(10, 0), default=0)
    losing_trades = Column(Numeric(10, 0), default=0)
    max_drawdown = Column(Numeric(10, 6), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="portfolio")
    balances = relationship("Balance", back_populates="portfolio")


class Balance(Base):
    __tablename__ = "balances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id"), nullable=False)
    asset = Column(String(20), nullable=False)
    quantity = Column(Numeric(20, 8), default=0)
    locked_quantity = Column(Numeric(20, 8), default=0)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    portfolio = relationship("Portfolio", back_populates="balances")
