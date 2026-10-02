from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from app.models.arbitrage import OpportunityStatus, RejectionReason
from app.models.trade import TradeStatus, TradeMode


class MarketDataSchema(BaseModel):
    symbol: str
    bid: Decimal
    ask: Decimal
    bid_quantity: Decimal
    ask_quantity: Decimal
    last_price: Optional[Decimal] = None
    timestamp: datetime
    exchange: str


class OpportunitySchema(BaseModel):
    id: str
    buy_exchange: str
    sell_exchange: str
    symbol: str
    buy_price: Decimal
    sell_price: Decimal
    gross_spread: Decimal
    gross_spread_percent: Decimal
    buy_fee: Decimal
    sell_fee: Decimal
    estimated_slippage: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    net_profit_percent: Decimal
    quantity: Decimal
    status: OpportunityStatus
    rejection_reason: Optional[RejectionReason] = None
    rejection_details: Optional[str] = None
    created_at: datetime


class TradeSchema(BaseModel):
    id: str
    symbol: str
    mode: TradeMode
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    quantity: Decimal
    buy_fee: Decimal
    sell_fee: Decimal
    slippage: Decimal
    network_cost: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    status: TradeStatus
    created_at: datetime
    executed_at: Optional[datetime] = None


class PortfolioSchema(BaseModel):
    id: str
    name: str
    initial_capital: Decimal
    current_capital: Decimal
    total_pnl: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: Decimal


class KillSwitchSchema(BaseModel):
    active: bool
    activated_at: Optional[datetime] = None
    reason: str = ""


class SystemStatusSchema(BaseModel):
    mode: str
    kill_switch_active: bool
    total_opportunities: int
    executable_opportunities: int
    rejected_opportunities: int
    total_trades: int
    today_pnl: Decimal
    total_pnl: Decimal
    win_rate: Decimal
    max_drawdown: Decimal
    exchanges_healthy: int
    exchanges_total: int
