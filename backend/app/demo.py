"""Demo mode: feeds simulated market data to demonstrate the dashboard."""
import asyncio
import random
from decimal import Decimal
from datetime import datetime, timezone
from app.market_data.engine import MarketDataEngine
from app.arbitrage.engine import ArbitrageEngine
from app.risk.manager import risk_manager
from app.paper_trading.engine import paper_trading_engine
from app.portfolio.tracker import portfolio_tracker
from app.exchanges.mock import MockExchangeAdapter
from app.exchanges.base import Ticker
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("demo")

# Simulated exchange pairs with realistic prices
DEMO_SYMBOLS = ["BTC/USDT", "ETH/USDT"]
BASE_PRICES = {
    "BTC/USDT": Decimal("84000"),
    "ETH/USDT": Decimal("3200"),
}
EXCHANGES = ["binance", "coinbase", "kraken"]

_all_opportunities = []


def get_all_opportunities():
    return _all_opportunities


async def run_demo():
    logger.info("demo_mode_starting", exchanges=EXCHANGES, symbols=DEMO_SYMBOLS)

    adapters = {}
    for name in EXCHANGES:
        adapter = MockExchangeAdapter(name)
        adapters[name] = adapter

    market_data = MarketDataEngine(stale_threshold_ms=5000)
    for name, adapter in adapters.items():
        market_data.register_exchange(name, adapter)

    arbitrage_engine = ArbitrageEngine(market_data)

    logger.info("demo_feeding_data")

    iteration = 0
    while True:
        iteration += 1
        now = datetime.now(timezone.utc)

        for symbol in DEMO_SYMBOLS:
            base_price = BASE_PRICES[symbol]

            for name, adapter in adapters.items():
                # Add realistic price variation per exchange
                exchange_offset = Decimal(str(random.uniform(-0.008, 0.008)))
                spread_pct = Decimal(str(random.uniform(0.0005, 0.002)))
                bid_offset = spread_pct / 2
                ask_offset = spread_pct / 2

                bid = base_price * (1 + exchange_offset - bid_offset)
                ask = base_price * (1 + exchange_offset + ask_offset)

                # Create arbitrage opportunities more often (40% of the time)
                if random.random() < 0.40:
                    scenario = random.choice(["wide_profit", "narrow_profit", "reversed"])
                    if scenario == "wide_profit":
                        # Exchange A is cheap, Exchange B is expensive — clear profit
                        if adapter.name == EXCHANGES[0]:
                            bid = base_price * Decimal("0.994")
                            ask = base_price * Decimal("0.995")
                        elif adapter.name == EXCHANGES[1]:
                            bid = base_price * Decimal("1.006")
                            ask = base_price * Decimal("1.007")
                        else:
                            bid = base_price * Decimal("0.999")
                            ask = base_price * Decimal("1.000")
                    elif scenario == "narrow_profit":
                        # Smaller but still profitable spread
                        if adapter.name == EXCHANGES[0]:
                            bid = base_price * Decimal("0.997")
                            ask = base_price * Decimal("0.998")
                        elif adapter.name == EXCHANGES[1]:
                            bid = base_price * Decimal("1.002")
                            ask = base_price * Decimal("1.003")
                        else:
                            bid = base_price * Decimal("0.9995")
                            ask = base_price * Decimal("1.0005")
                    else:
                        # Reversed — creates opportunity for the third exchange
                        if adapter.name == EXCHANGES[0]:
                            bid = base_price * Decimal("1.005")
                            ask = base_price * Decimal("1.006")
                        elif adapter.name == EXCHANGES[1]:
                            bid = base_price * Decimal("0.993")
                            ask = base_price * Decimal("0.994")
                        else:
                            bid = base_price * Decimal("0.998")
                            ask = base_price * Decimal("0.999")

                bid_qty = Decimal(str(random.uniform(0.01, 0.1)))
                ask_qty = Decimal(str(random.uniform(0.01, 0.1)))

                ticker = Ticker(
                    symbol=symbol,
                    bid=bid.quantize(Decimal("0.01")),
                    ask=ask.quantize(Decimal("0.01")),
                    bid_quantity=bid_qty.quantize(Decimal("0.001")),
                    ask_quantity=ask_qty.quantize(Decimal("0.001")),
                    last_price=((bid + ask) / 2).quantize(Decimal("0.01")),
                    timestamp=now,
                )
                market_data.set_ticker(name, symbol, ticker)

        # Scan for opportunities
        all_opps = arbitrage_engine.scan_all(DEMO_SYMBOLS)

        executable = [o for o in all_opps if o.is_executable]
        rejected = [o for o in all_opps if not o.is_executable]

        _all_opportunities.clear()
        for opp in all_opps:
            _all_opportunities.append({
                "id": f"opp-{iteration}-{random.randint(1000,9999)}",
                "buy_exchange": opp.buy_exchange,
                "sell_exchange": opp.sell_exchange,
                "symbol": opp.symbol,
                "buy_price": str(opp.buy_price),
                "sell_price": str(opp.sell_price),
                "gross_spread": str(opp.gross_spread),
                "gross_spread_percent": str(opp.gross_spread_percent.quantize(Decimal("0.01"))),
                "buy_fee": str(opp.buy_fee.quantize(Decimal("0.01"))),
                "sell_fee": str(opp.sell_fee.quantize(Decimal("0.01"))),
                "estimated_slippage": str(opp.estimated_slippage.quantize(Decimal("0.01"))),
                "total_cost": str(opp.total_cost.quantize(Decimal("0.01"))),
                "gross_profit": str(opp.gross_profit.quantize(Decimal("0.01"))),
                "net_profit": str(opp.net_profit.quantize(Decimal("0.01"))),
                "net_profit_percent": str(opp.net_profit_percent.quantize(Decimal("0.01"))),
                "quantity": str(opp.quantity.quantize(Decimal("0.001"))),
                "status": "executable" if opp.is_executable else "rejected",
                "rejection_reason": opp.rejection_reason,
                "rejection_details": opp.rejection_details,
                "created_at": now.isoformat(),
            })

        # Execute profitable trades in paper mode
        if executable and settings.TRADING_MODE.value in ("paper", "scanner"):
            best = executable[0]
            if settings.TRADING_MODE.value == "paper":
                risk_check = await risk_manager.check_trade(
                    trade_amount=best.quantity * best.buy_price,
                    expected_profit=best.net_profit,
                    current_capital=Decimal(str(paper_trading_engine.capital)),
                )
                if risk_check.approved:
                    result = await paper_trading_engine.execute_trade(
                        symbol=best.symbol,
                        buy_exchange=best.buy_exchange,
                        sell_exchange=best.sell_exchange,
                        buy_price=best.buy_price,
                        sell_price=best.sell_price,
                        quantity=best.quantity,
                        buy_fee=best.buy_fee,
                        sell_fee=best.sell_fee,
                        slippage=best.estimated_slippage,
                    )
                    if result.get("success"):
                        risk_manager.record_trade_open(best.quantity * best.buy_price)
                        risk_manager.record_trade_close(
                            best.quantity * best.buy_price,
                            Decimal(result.get("net_profit", "0")),
                        )
                        portfolio_tracker.record_trade(
                            trade_id=result["trade_id"],
                            symbol=best.symbol,
                            buy_exchange=best.buy_exchange,
                            sell_exchange=best.sell_exchange,
                            buy_price=best.buy_price,
                            sell_price=best.sell_price,
                            quantity=best.quantity,
                            fees=best.buy_fee + best.sell_fee,
                            net_profit=Decimal(result.get("net_profit", "0")),
                            mode="paper",
                        )
                        logger.info(
                            "demo_trade_executed",
                            symbol=best.symbol,
                            net_profit=result.get("net_profit"),
                        )

        logger.info(
            "demo_scan_complete",
            iteration=iteration,
            total=len(all_opps),
            executable=len(executable),
            rejected=len(rejected),
            capital=str(paper_trading_engine.capital),
        )

        await asyncio.sleep(3)
