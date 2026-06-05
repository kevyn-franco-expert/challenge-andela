from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.infrastructure.database import init_db
from app.core.logging_config import setup_logging
from app.interfaces.api.middleware import LoggingMiddleware
from app.interfaces.api.routers import health, logs, anomalies, alerts, dashboard

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Intelligent Observability & Event Watchdog",
    description="API-first SRE observability platform with AI-driven anomaly detection.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(health.router)
app.include_router(logs.router)
app.include_router(anomalies.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
