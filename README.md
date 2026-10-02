# BB-ARBITRAGE

A research, paper-trading, and risk-controlled crypto arbitrage platform.

**IMPORTANT DISCLAIMER**: This is a research and paper-trading platform. It is NOT a guaranteed-profit system. Past performance does not guarantee future results. Arbitrage opportunities may disappear. Fees, slippage, liquidity, and execution risk can eliminate expected profits.

## Features

- Real-time market data collection via WebSocket
- Arbitrage opportunity detection across exchanges
- Complete cost calculation (fees, slippage, network costs)
- Risk engine with configurable limits
- Paper trading simulator
- Historical backtesting
- Portfolio and P&L tracking
- Kill switch for emergency stop
- Complete audit trail
- Prometheus metrics and Grafana dashboards

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                     │
└──────────────────────┬──────────────────────────────────┘
                       │ REST / WebSocket
┌──────────────────────▼──────────────────────────────────┐
│                  API Layer (FastAPI)                      │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                   Core Services                          │
│  Market Data → Arbitrage Engine → Risk Engine            │
│  Exchange Adapters → Paper Trading → Portfolio           │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              Infrastructure                              │
│  PostgreSQL │ Redis │ Prometheus │ Grafana               │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12+, FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Infrastructure**: Docker, Docker Compose, Nginx
- **Monitoring**: Prometheus, Grafana

## Quick Start

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- PostgreSQL (or use Docker)
- Redis (or use Docker)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bb-arbitrage
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the API:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Development Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest tests/ -v
```

4. Start development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| TRADING_MODE | paper | scanner, paper, or live |
| INITIAL_CAPITAL_INR | 100 | Starting capital in INR |
| MAX_TRADE_AMOUNT_INR | 10 | Maximum per trade |
| MAX_DAILY_LOSS_INR | 2 | Daily loss limit |
| MAX_OPEN_TRADES | 1 | Maximum concurrent trades |
| MAX_TRADES_PER_DAY | 5 | Daily trade limit |
| MIN_NET_PROFIT_INR | 0.10 | Minimum profit to execute |
| STALE_DATA_MS | 500 | Market data freshness |
| LIVE_TRADING_ENABLED | false | Enable live trading |

### Trading Modes

1. **SCANNER**: Detect opportunities only, no execution
2. **PAPER**: Simulate execution with realistic conditions
3. **LIVE**: Actual exchange orders (disabled by default)

## Risk Management

The system includes multiple risk controls:

- Maximum trade size limits
- Daily loss limits
- Maximum open positions
- Market data freshness checks
- Exchange health monitoring
- Global kill switch

### Kill Switch

Emergency stop endpoint:
```bash
# Activate
curl -X POST http://localhost:8000/api/risk/kill-switch \
  -H "Content-Type: application/json" \
  -d '{"reason": "Emergency stop"}'

# Deactivate
curl -X DELETE http://localhost:8000/api/risk/kill-switch
```

## API Endpoints

- `GET /api/health/` - System health
- `GET /api/market-data/status` - Market data status
- `GET /api/opportunities/` - List opportunities
- `GET /api/trading/status` - Trading status
- `GET /api/portfolio/` - Portfolio summary
- `GET /api/risk/status` - Risk status
- `POST /api/risk/kill-switch` - Activate kill switch

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_arbitrage.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## Security

- Exchange API keys are never exposed to the frontend
- All secrets are stored in environment variables
- No withdrawal functionality is implemented
- Authentication required for all endpoints
- Input validation on all API requests

## Limitations

- This is a research platform, not a profit guarantee
- Paper trading results may differ from live trading
- Arbitrage opportunities are often temporary
- Network latency can affect execution
- Market conditions change rapidly

## Tax/Accounting

This platform provides transaction records for your analysis. It does NOT provide tax advice. Consult a qualified tax professional for your jurisdiction.

## License

[License File]
