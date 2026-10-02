from prometheus_client import Counter, Histogram, Gauge, Summary

opportunities_detected = Counter(
    "bb_opportunities_detected_total",
    "Total arbitrage opportunities detected",
    ["symbol"]
)

opportunities_rejected = Counter(
    "bb_opportunities_rejected_total",
    "Total arbitrage opportunities rejected",
    ["symbol", "reason"]
)

trades_executed = Counter(
    "bb_trades_executed_total",
    "Total trades executed",
    ["mode", "symbol"]
)

trade_errors = Counter(
    "bb_trade_errors_total",
    "Total trade errors",
    ["error_type"]
)

market_data_latency = Histogram(
    "bb_market_data_latency_seconds",
    "Market data latency in seconds",
    ["exchange"]
)

api_latency = Histogram(
    "bb_api_latency_seconds",
    "API request latency in seconds",
    ["endpoint"]
)

pnl = Gauge(
    "bb_pnl",
    "Current profit and loss",
    ["period"]
)

drawdown = Gauge(
    "bb_drawdown",
    "Current drawdown percentage"
)

risk_events = Counter(
    "bb_risk_events_total",
    "Total risk events",
    ["event_type"]
)

websocket_disconnects = Counter(
    "bb_websocket_disconnects_total",
    "Total WebSocket disconnections",
    ["exchange"]
)

active_trades = Gauge(
    "bb_active_trades",
    "Number of active trades"
)

capital = Gauge(
    "bb_capital",
    "Current capital"
)
