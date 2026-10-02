"""Stock data service using yfinance (free, unlimited)."""
import asyncio
from decimal import Decimal
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Optional
from app.core.logging import get_logger

logger = get_logger("stocks")

# Indian stocks: Yahoo Finance uses .NS (NSE) and .BO (BSE) suffixes
INDIAN_STOCKS = {
    "RELIANCE": {"name": "Reliance Industries", "sector": "Oil & Gas", "bse": "RELIANCE.BO", "nse": "RELIANCE.NS"},
    "TCS": {"name": "Tata Consultancy Services", "sector": "IT", "bse": "TCS.BO", "nse": "TCS.NS"},
    "INFY": {"name": "Infosys", "sector": "IT", "bse": "INFY.BO", "nse": "INFY.NS"},
    "HDFCBANK": {"name": "HDFC Bank", "sector": "Banking", "bse": "HDFCBANK.BO", "nse": "HDFCBANK.NS"},
    "ICICIBANK": {"name": "ICICI Bank", "sector": "Banking", "bse": "ICICIBANK.BO", "nse": "ICICIBANK.NS"},
    "SBIN": {"name": "State Bank of India", "sector": "Banking", "bse": "SBIN.BO", "nse": "SBIN.NS"},
    "BHARTIARTL": {"name": "Bharti Airtel", "sector": "Telecom", "bse": "BHARTIARTL.BO", "nse": "BHARTIARTL.NS"},
    "ITC": {"name": "ITC Limited", "sector": "FMCG", "bse": "ITC.BO", "nse": "ITC.NS"},
    "KOTAKBANK": {"name": "Kotak Mahindra Bank", "sector": "Banking", "bse": "KOTAKBANK.BO", "nse": "KOTAKBANK.NS"},
    "LT": {"name": "Larsen & Toubro", "sector": "Infrastructure", "bse": "LT.BO", "nse": "LT.NS"},
    "AXISBANK": {"name": "Axis Bank", "sector": "Banking", "bse": "AXISBANK.BO", "nse": "AXISBANK.NS"},
    "WIPRO": {"name": "Wipro", "sector": "IT", "bse": "WIPRO.BO", "nse": "WIPRO.NS"},
    "TATAMOTORS": {"name": "Tata Motors", "sector": "Auto", "bse": "TATAMOTORS.BO", "nse": "TATAMOTORS.NS"},
    "SUNPHARMA": {"name": "Sun Pharma", "sector": "Pharma", "bse": "SUNPHARMA.BO", "nse": "SUNPHARMA.NS"},
    "ADANIENT": {"name": "Adani Enterprises", "sector": "Conglomerate", "bse": "ADANIENT.BO", "nse": "ADANIENT.NS"},
    "TATASTEEL": {"name": "Tata Steel", "sector": "Metal", "bse": "TATASTEEL.BO", "nse": "TATASTEEL.NS"},
    "ONGC": {"name": "Oil & Natural Gas Corp", "sector": "Oil & Gas", "bse": "ONGC.BO", "nse": "ONGC.NS"},
    "NTPC": {"name": "NTPC", "sector": "Power", "bse": "NTPC.BO", "nse": "NTPC.NS"},
    "POWERGRID": {"name": "Power Grid Corp", "sector": "Power", "bse": "POWERGRID.BO", "nse": "POWERGRID.NS"},
    "HCLTECH": {"name": "HCL Technologies", "sector": "IT", "bse": "HCLTECH.BO", "nse": "HCLTECH.NS"},
    "BAJFINANCE": {"name": "Bajaj Finance", "sector": "Finance", "bse": "BAJFINANCE.BO", "nse": "BAJFINANCE.NS"},
    "MARUTI": {"name": "Maruti Suzuki", "sector": "Auto", "bse": "MARUTI.BO", "nse": "MARUTI.NS"},
    "TITAN": {"name": "Titan Company", "sector": "Consumer", "bse": "TITAN.BO", "nse": "TITAN.NS"},
    "ASIANPAINT": {"name": "Asian Paints", "sector": "Consumer", "bse": "ASIANPAINT.BO", "nse": "ASIANPAINT.NS"},
    "ULTRACEMCO": {"name": "UltraTech Cement", "sector": "Cement", "bse": "ULTRACEMCO.BO", "nse": "ULTRACEMCO.NS"},
    "NESTLEIND": {"name": "Nestle India", "sector": "FMCG", "bse": "NESTLEIND.BO", "nse": "NESTLEIND.NS"},
    "TECHM": {"name": "Tech Mahindra", "sector": "IT", "bse": "TECHM.BO", "nse": "TECHM.NS"},
    "DRREDDY": {"name": "Dr. Reddy's Labs", "sector": "Pharma", "bse": "DRREDDY.BO", "nse": "DRREDDY.NS"},
    "CIPLA": {"name": "Cipla", "sector": "Pharma", "bse": "CIPLA.BO", "nse": "CIPLA.NS"},
    "DIVISLAB": {"name": "Divi's Labs", "sector": "Pharma", "bse": "DIVISLAB.BO", "nse": "DIVISLAB.NS"},
    "EICHERMOT": {"name": "Eicher Motors", "sector": "Auto", "bse": "EICHERMOT.BO", "nse": "EICHERMOT.NS"},
    "BAJAJFINSV": {"name": "Bajaj Finserv", "sector": "Finance", "bse": "BAJAJFINSV.BO", "nse": "BAJAJFINSV.NS"},
    "HEROMOTOCO": {"name": "Hero MotoCorp", "sector": "Auto", "bse": "HEROMOTOCO.BO", "nse": "HEROMOTOCO.NS"},
    "BRITANNIA": {"name": "Britannia Industries", "sector": "FMCG", "bse": "BRITANNIA.BO", "nse": "BRITANNIA.NS"},
    "INDUSINDBK": {"name": "IndusInd Bank", "sector": "Banking", "bse": "INDUSINDBK.BO", "nse": "INDUSINDBK.NS"},
    "BPCL": {"name": "Bharat Petroleum", "sector": "Oil & Gas", "bse": "BPCL.BO", "nse": "BPCL.NS"},
    "COALINDIA": {"name": "Coal India", "sector": "Mining", "bse": "COALINDIA.BO", "nse": "COALINDIA.NS"},
    "GRASIM": {"name": "Grasim Industries", "sector": "Cement", "bse": "GRASIM.BO", "nse": "GRASIM.NS"},
    "TATACONSUM": {"name": "Tata Consumer Products", "sector": "FMCG", "bse": "TATACONSUM.BO", "nse": "TATACONSUM.NS"},
    "APOLLOHOSP": {"name": "Apollo Hospitals", "sector": "Healthcare", "bse": "APOLLOHOSP.BO", "nse": "APOLLOHOSP.NS"},
}

# Affordable Indian stocks (likely under ₹500)
AFFORDABLE_INDIAN = [
    "YESBANK", "VODAFONEIDEA", "PNB", "BANKBARODA", "CANBK",
    "IDBI", "IOB", "UNIONBANK", "INDIANB", "UCO",
    "RECLTD", "PFC", "NHPC", "SJVN", "IRFC",
    "HAL", "BEL", "BDL", "COCHINSHIP", "MAZAGON",
    "TATAPOWER", "ADANIGREEN", "ADANIPORTS", "BALRAMPUR", "RAIN",
    "RENUKA", "DALBHARAT", "DEEPAKNTR", "LAURUSLABS", "ALLEN",
]

# US stocks
US_STOCKS = {
    "AAPL": {"name": "Apple Inc", "sector": "Technology"},
    "MSFT": {"name": "Microsoft", "sector": "Technology"},
    "GOOGL": {"name": "Alphabet (Google)", "sector": "Technology"},
    "AMZN": {"name": "Amazon", "sector": "E-Commerce"},
    "NVDA": {"name": "NVIDIA", "sector": "Semiconductors"},
    "META": {"name": "Meta (Facebook)", "sector": "Technology"},
    "TSLA": {"name": "Tesla", "sector": "Electric Vehicles"},
    "AMD": {"name": "AMD", "sector": "Semiconductors"},
    "NFLX": {"name": "Netflix", "sector": "Entertainment"},
    "COIN": {"name": "Coinbase", "sector": "Crypto"},
    "SOFI": {"name": "SoFi Technologies", "sector": "Fintech"},
    "NIO": {"name": "NIO Inc", "sector": "Electric Vehicles"},
    "PLTR": {"name": "Palantir", "sector": "Data Analytics"},
    "SQ": {"name": "Block (Square)", "sector": "Fintech"},
    "ROKU": {"name": "Roku", "sector": "Entertainment"},
    "SNAP": {"name": "Snap Inc", "sector": "Social Media"},
    "UBER": {"name": "Uber", "sector": "Transportation"},
    "LYFT": {"name": "Lyft", "sector": "Transportation"},
    "ABNB": {"name": "Airbnb", "sector": "Travel"},
    "HOOD": {"name": "Robinhood", "sector": "Fintech"},
    "RIVN": {"name": "Rivian", "sector": "Electric Vehicles"},
    "LCID": {"name": "Lucid Motors", "sector": "Electric Vehicles"},
    "DNA": {"name": "Ginkgo Bioworks", "sector": "Biotech"},
    "CLOV": {"name": "Clover Health", "sector": "Healthcare"},
    "WISH": {"name": "ContextLogic", "sector": "E-Commerce"},
}


@dataclass
class StockPrice:
    symbol: str
    name: str
    market: str  # "NSE", "BSE", "NYSE", "NASDAQ"
    price: Decimal
    currency: str
    volume: int
    change_pct: Decimal
    timestamp: datetime


@dataclass
class BSENSpread:
    symbol: str
    name: str
    nse_price: Decimal
    bse_price: Decimal
    spread: Decimal
    spread_pct: Decimal
    buy_exchange: str
    sell_exchange: str
    profitable: bool


class StockDataService:
    def __init__(self):
        self._cache: dict[str, StockPrice] = {}
        self._spread_cache: dict[str, BSENSpread] = {}
        self._last_fetch: dict[str, datetime] = {}

    async def get_stock_price(self, symbol: str, market: str = "auto") -> Optional[StockPrice]:
        try:
            import yfinance as yf

            ticker_map = {
                "NSE": f"{symbol}.NS",
                "BSE": f"{symbol}.BO",
                "NYSE": symbol,
                "NASDAQ": symbol,
            }

            if market == "auto":
                # Try NSE first for Indian stocks, then US
                if symbol in INDIAN_STOCKS:
                    yahoo_symbol = f"{symbol}.NS"
                    market = "NSE"
                elif symbol in US_STOCKS:
                    yahoo_symbol = symbol
                    market = "NYSE"
                else:
                    yahoo_symbol = f"{symbol}.NS"
                    market = "NSE"
            else:
                yahoo_symbol = ticker_map.get(market, symbol)

            def fetch():
                ticker = yf.Ticker(yahoo_symbol)
                info = ticker.fast_info
                price = Decimal(str(info.last_price)) if hasattr(info, 'last_price') else Decimal("0")
                volume = int(info.last_volume) if hasattr(info, 'last_volume') else 0
                prev_close = Decimal(str(info.previous_close)) if hasattr(info, 'previous_close') else price
                change_pct = ((price - prev_close) / prev_close * 100) if prev_close > 0 else Decimal("0")

                name = symbol
                if symbol in INDIAN_STOCKS:
                    name = INDIAN_STOCKS[symbol]["name"]
                elif symbol in US_STOCKS:
                    name = US_STOCKS[symbol]["name"]

                return StockPrice(
                    symbol=symbol,
                    name=name,
                    market=market,
                    price=price,
                    currency="INR" if market in ("NSE", "BSE") else "USD",
                    volume=volume,
                    change_pct=change_pct.quantize(Decimal("0.01")),
                    timestamp=datetime.now(timezone.utc),
                )

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, fetch)
            self._cache[f"{symbol}_{market}"] = result
            return result

        except Exception as e:
            logger.error("stock_price_error", symbol=symbol, market=market, error=str(e))
            return None

    async def get_bse_nse_spread(self, symbol: str) -> Optional[BSENSpread]:
        try:
            nse_price = await self.get_stock_price(symbol, "NSE")
            bse_price = await self.get_stock_price(symbol, "BSE")

            if not nse_price or not bse_price or nse_price.price == 0 or bse_price.price == 0:
                return None

            if nse_price.price > bse_price.price:
                spread = nse_price.price - bse_price.price
                buy_exchange = "BSE"
                sell_exchange = "NSE"
            else:
                spread = bse_price.price - nse_price.price
                buy_exchange = "NSE"
                sell_exchange = "BSE"

            spread_pct = (spread / min(nse_price.price, bse_price.price)) * 100

            # Indian brokerage: ~0.25% total cost
            total_cost_pct = Decimal("0.25")
            profitable = spread_pct > total_cost_pct

            result = BSENSpread(
                symbol=symbol,
                name=INDIAN_STOCKS.get(symbol, {}).get("name", symbol),
                nse_price=nse_price.price,
                bse_price=bse_price.price,
                spread=spread.quantize(Decimal("0.01")),
                spread_pct=spread_pct.quantize(Decimal("0.01")),
                buy_exchange=buy_exchange,
                sell_exchange=sell_exchange,
                profitable=profitable,
            )
            self._spread_cache[symbol] = result
            return result

        except Exception as e:
            logger.error("bse_nse_spread_error", symbol=symbol, error=str(e))
            return None

    async def scan_affordable_stocks(self, max_price_inr: Decimal = Decimal("500"), market: str = "indian") -> list[StockPrice]:
        results = []

        if market in ("indian", "both"):
            for symbol in AFFORDABLE_INDIAN + list(INDIAN_STOCKS.keys()):
                price = await self.get_stock_price(symbol, "NSE")
                if price and price.price > 0 and price.price <= max_price_inr:
                    results.append(price)
                await asyncio.sleep(0.1)

        if market in ("us", "both"):
            for symbol in US_STOCKS:
                price = await self.get_stock_price(symbol, "NYSE")
                if price and price.price > 0:
                    price_inr = price.price * Decimal("85")
                    if price_inr <= max_price_inr:
                        results.append(price)
                await asyncio.sleep(0.1)

        results.sort(key=lambda x: x.price)
        return results

    async def auto_discover_arbitrage(self, max_price_inr: Decimal = Decimal("500")) -> list[BSENSpread]:
        results = []
        for symbol in AFFORDABLE_INDIAN + list(INDIAN_STOCKS.keys()):
            spread = await self.get_bse_nse_spread(symbol)
            if spread and spread.spread_pct > Decimal("0.1"):
                results.append(spread)
            await asyncio.sleep(0.2)

        results.sort(key=lambda x: x.spread_pct, reverse=True)
        return results

    def get_watched_stocks(self) -> dict:
        return {
            "indian": INDIAN_STOCKS,
            "us": US_STOCKS,
            "affordable": AFFORDABLE_INDIAN,
        }


stock_service = StockDataService()
