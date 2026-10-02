from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timezone
from typing import Optional
from app.market_data.engine import MarketDataEngine
from app.exchanges.base import Ticker
from app.core.logging import get_logger
from app.config.settings import settings

logger = get_logger("arbitrage")


@dataclass
class ArbitrageOpportunityResult:
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    gross_spread: Decimal
    gross_spread_percent: Decimal
    buy_fee: Decimal
    sell_fee: Decimal
    estimated_slippage: Decimal
    network_cost: Decimal
    other_costs: Decimal
    total_cost: Decimal
    gross_profit: Decimal
    net_profit: Decimal
    net_profit_percent: Decimal
    quantity: Decimal
    is_executable: bool
    rejection_reason: Optional[str] = None
    rejection_details: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)


class ArbitrageEngine:
    def __init__(self, market_data: MarketDataEngine):
        self.market_data = market_data
        self._fee_cache: dict[str, tuple[Decimal, Decimal]] = {}
        self._min_profit = settings.MIN_NET_PROFIT_INR
        self._min_profit_pct = Decimal(str(settings.MIN_NET_PROFIT_PERCENT))
        self._max_slippage = Decimal(str(settings.MAX_SLIPPAGE_PERCENT))

    def set_fee(self, exchange: str, maker: Decimal, taker: Decimal) -> None:
        self._fee_cache[exchange] = (maker, taker)

    def _get_fee(self, exchange: str) -> Decimal:
        if exchange in self._fee_cache:
            return self._fee_cache[exchange][1]
        return Decimal("0.001")

    def _estimate_slippage(self, ticker: Ticker, quantity: Decimal) -> Decimal:
        if ticker.ask_quantity == 0:
            return Decimal("1")
        slippage_ratio = quantity / ticker.ask_quantity
        return min(slippage_ratio * Decimal("0.01"), self._max_slippage)

    def _estimate_network_cost(self) -> Decimal:
        return Decimal("0.10")

    def scan_pair(self, symbol: str) -> list[ArbitrageOpportunityResult]:
        opportunities = []
        tickers = self.market_data.get_all_tickers(symbol)
        exchanges = list(tickers.keys())

        for i, buy_exchange in enumerate(exchanges):
            for j, sell_exchange in enumerate(exchanges):
                if i >= j:
                    continue

                buy_ticker = tickers[buy_exchange]
                sell_ticker = tickers[sell_exchange]

                if not buy_ticker or not sell_ticker:
                    continue

                if self.market_data.is_stale(buy_exchange, symbol):
                    continue
                if self.market_data.is_stale(sell_exchange, symbol):
                    continue

                result = self._evaluate_opportunity(
                    symbol, buy_exchange, sell_exchange, buy_ticker, sell_ticker
                )
                if result:
                    opportunities.append(result)

        opportunities.sort(key=lambda x: x.net_profit, reverse=True)
        return opportunities

    def _evaluate_opportunity(
        self,
        symbol: str,
        buy_exchange: str,
        sell_exchange: str,
        buy_ticker: Ticker,
        sell_ticker: Ticker,
    ) -> Optional[ArbitrageOpportunityResult]:
        buy_price = buy_ticker.ask
        sell_price = sell_ticker.bid

        if sell_price <= buy_price:
            return ArbitrageOpportunityResult(
                symbol=symbol,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                buy_price=buy_price,
                sell_price=sell_price,
                gross_spread=Decimal("0"),
                gross_spread_percent=Decimal("0"),
                buy_fee=Decimal("0"),
                sell_fee=Decimal("0"),
                estimated_slippage=Decimal("0"),
                network_cost=Decimal("0"),
                other_costs=Decimal("0"),
                total_cost=Decimal("0"),
                gross_profit=Decimal("0"),
                net_profit=Decimal("0"),
                net_profit_percent=Decimal("0"),
                quantity=Decimal("0"),
                is_executable=False,
                rejection_reason="SPREAD_TOO_SMALL",
                rejection_details="Sell price <= buy price",
            )

        gross_spread = sell_price - buy_price
        gross_spread_percent = (gross_spread / buy_price) * 100

        quantity = min(buy_ticker.ask_quantity, sell_ticker.bid_quantity) * Decimal("0.1")
        if quantity * buy_price < Decimal("1"):
            return ArbitrageOpportunityResult(
                symbol=symbol,
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                buy_price=buy_price,
                sell_price=sell_price,
                gross_spread=gross_spread,
                gross_spread_percent=gross_spread_percent,
                buy_fee=Decimal("0"),
                sell_fee=Decimal("0"),
                estimated_slippage=Decimal("0"),
                network_cost=Decimal("0"),
                other_costs=Decimal("0"),
                total_cost=Decimal("0"),
                gross_profit=Decimal("0"),
                net_profit=Decimal("0"),
                net_profit_percent=Decimal("0"),
                quantity=quantity,
                is_executable=False,
                rejection_reason="INSUFFICIENT_LIQUIDITY",
                rejection_details=f"Insufficient liquidity: {quantity}",
            )

        buy_fee_rate = self._get_fee(buy_exchange)
        sell_fee_rate = self._get_fee(sell_exchange)
        buy_fee = buy_price * quantity * buy_fee_rate
        sell_fee = sell_price * quantity * sell_fee_rate

        slippage_pct = self._estimate_slippage(buy_ticker, quantity)
        slippage = buy_price * quantity * slippage_pct

        network_cost = self._estimate_network_cost()
        other_costs = Decimal("0")

        total_cost = buy_fee + sell_fee + slippage + network_cost + other_costs
        gross_profit = (sell_price - buy_price) * quantity
        net_profit = gross_profit - total_cost

        net_profit_percent = (net_profit / (buy_price * quantity)) * 100 if buy_price * quantity > 0 else Decimal("0")

        rejection_reason = None
        rejection_details = None
        is_executable = True

        if net_profit < self._min_profit:
            is_executable = False
            rejection_reason = "NET_PROFIT_BELOW_THRESHOLD"
            rejection_details = f"Net profit {net_profit} < minimum {self._min_profit}"
        elif net_profit_percent < self._min_profit_pct:
            is_executable = False
            rejection_reason = "NET_PROFIT_BELOW_THRESHOLD"
            rejection_details = f"Net profit % {net_profit_percent} < minimum {self._min_profit_pct}%"

        return ArbitrageOpportunityResult(
            symbol=symbol,
            buy_exchange=buy_exchange,
            sell_exchange=sell_exchange,
            buy_price=buy_price,
            sell_price=sell_price,
            gross_spread=gross_spread,
            gross_spread_percent=gross_spread_percent,
            buy_fee=buy_fee,
            sell_fee=sell_fee,
            estimated_slippage=slippage,
            network_cost=network_cost,
            other_costs=other_costs,
            total_cost=total_cost,
            gross_profit=gross_profit,
            net_profit=net_profit,
            net_profit_percent=net_profit_percent,
            quantity=quantity,
            is_executable=is_executable,
            rejection_reason=rejection_reason,
            rejection_details=rejection_details,
        )

    def scan_all(self, symbols: list[str]) -> list[ArbitrageOpportunityResult]:
        all_opportunities = []
        for symbol in symbols:
            opportunities = self.scan_pair(symbol)
            all_opportunities.extend(opportunities)
        all_opportunities.sort(key=lambda x: x.net_profit, reverse=True)
        return all_opportunities
