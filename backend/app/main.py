from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.config.settings import settings
from app.api.router import api_router
from app.core.logging import get_logger

logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "app_starting",
        env=settings.APP_ENV,
        mode=settings.TRADING_MODE.value,
        live_enabled=settings.LIVE_TRADING_ENABLED,
    )
    yield
    logger.info("app_shutting_down")


app = FastAPI(
    title="BB-ARBITRAGE",
    description="Crypto Arbitrage Research & Paper Trading Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if settings.PROMETHEUS_ENABLED:
    Instrumentator().instrument(app).expose(app)


@app.get("/")
async def root():
    return {
        "name": "BB-ARBITRAGE",
        "version": "1.0.0",
        "mode": settings.TRADING_MODE.value,
        "live_trading_enabled": settings.LIVE_TRADING_ENABLED,
        "docs": "/docs" if settings.DEBUG else None,
    }
