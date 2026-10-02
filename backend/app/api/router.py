from fastapi import APIRouter
from app.api import market_data, opportunities, trading, portfolio, risk, backtesting, health, demo, stocks, options

api_router = APIRouter(prefix="/api")

api_router.include_router(market_data.router, prefix="/market-data", tags=["Market Data"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
api_router.include_router(trading.router, prefix="/trading", tags=["Trading"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["Portfolio"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk"])
api_router.include_router(backtesting.router, prefix="/backtesting", tags=["Backtesting"])
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(demo.router, prefix="/demo", tags=["Demo"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["Stocks"])
api_router.include_router(options.router, prefix="/options", tags=["Options"])
