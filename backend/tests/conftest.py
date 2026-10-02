import pytest
from decimal import Decimal
from app.exchanges.mock import MockExchangeAdapter
from app.exchanges.base import Ticker, OrderBook, OrderBookLevel
from app.market_data.engine import MarketDataEngine
from app.arbitrage.engine import ArbitrageEngine
from app.risk.manager import RiskManager
from app.paper_trading.engine import PaperTradingEngine
from app.portfolio.tracker import PortfolioTracker
from app.backtesting.engine import BacktestingEngine, BacktestConfig


@pytest.fixture
def mock_exchange():
    return MockExchangeAdapter(name="test_exchange")


@pytest.fixture
def market_data_engine():
    engine = MarketDataEngine(stale_threshold_ms=5000)
    return engine


@pytest.fixture
def arbitrage_engine(market_data_engine):
    return ArbitrageEngine(market_data_engine)


@pytest.fixture
def risk_manager():
    return RiskManager()


@pytest.fixture
def paper_trading_engine():
    return PaperTradingEngine()


@pytest.fixture
def portfolio_tracker():
    return PortfolioTracker()


@pytest.fixture
def backtesting_engine():
    config = BacktestConfig(
        initial_capital=Decimal("100"),
        max_trade_amount=Decimal("10"),
        min_net_profit=Decimal("0.01"),
        fee_rate=Decimal("0.001"),
        slippage_rate=Decimal("0.0005"),
    )
    return BacktestingEngine(config)
