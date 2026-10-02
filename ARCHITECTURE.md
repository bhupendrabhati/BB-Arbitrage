# BB-ARBITRAGE Architecture

## Overview

BB-ARBITRAGE is a research, paper-trading, and risk-controlled crypto arbitrage platform. It is NOT a guaranteed-profit system. It calculates all known costs before considering an opportunity executable.

## System Modes

| Mode | Description | Default |
|------|-------------|---------|
| SCANNER | Detect opportunities only | - |
| PAPER | Simulate execution | **Yes** |
| LIVE | Actual exchange orders | **Disabled** |

LIVE mode requires explicit configuration, confirmation, risk limits, and exchange API credentials. Withdrawal permissions are NEVER required.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                     │
│  Dashboard │ Opportunities │ Trades │ Portfolio │ Risk    │
└──────────────────────┬──────────────────────────────────┘
                       │ REST / WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                  API Layer (FastAPI)                      │
│  Auth │ REST Endpoints │ WebSocket Manager               │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   Core Services                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Market   │  │Arbitrage │  │   Risk   │              │
│  │  Data    │→ │  Engine  │→ │  Engine  │              │
│  │  Engine  │  │          │  │          │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│       ↑              ↓              ↓                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │Exchange  │  │  Paper   │  │Portfolio │              │
│  │ Adapters │  │ Trading  │  │ Tracker  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Infrastructure                              │
│  PostgreSQL │ Redis │ Prometheus │ Grafana               │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

1. **Market Data Engine** collects real-time data via WebSocket from exchanges
2. **Arbitrage Engine** detects opportunities by comparing prices across exchanges
3. **Cost Calculator** computes gross spread, fees, slippage, network costs
4. **Risk Engine** validates against limits before execution
5. **Execution Layer** (Paper or Live) processes the trade
6. **Portfolio Tracker** updates positions and P&L
7. **Audit Logger** records every event

## Key Principles

- **Capital Preservation First**: Never risk more than configured limits
- **Fail Closed**: If uncertain, do not trade
- **Deterministic Calculations**: No randomness in profit estimation
- **No Stale Data**: Reject market data older than configured threshold
- **Complete Audit Trail**: Every decision is logged with reasoning

## Exchange Architecture

```
ExchangeAdapter (Interface)
├── BinanceAdapter
├── CoinbaseAdapter
├── KrakenAdapter
└── MockExchangeAdapter (for testing)
```

Each adapter implements: `get_ticker()`, `get_order_book()`, `get_balances()`, `create_order()`, `cancel_order()`, `get_order_status()`, `get_trading_fees()`, `get_symbol_rules()`

## Risk Controls

- Maximum trade amount
- Maximum daily loss
- Maximum open trades
- Maximum trades per day
- Minimum net profit threshold
- Maximum slippage tolerance
- Market data freshness check
- Exchange health monitoring
- Global kill switch

## Security

- Exchange secrets never exposed to frontend
- Environment variables / AWS Secrets Manager
- No API keys, secrets, passwords, or tokens in logs
- Authentication and role-based permissions
- No withdrawal functionality
