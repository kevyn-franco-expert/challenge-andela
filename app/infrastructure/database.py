from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, ForeignKey
from datetime import datetime
from app.core.config import settings

Base = declarative_base()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class LogEntryORM(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    service = Column(String(255), nullable=False, index=True)
    level = Column(String(50), nullable=False, index=True)
    message = Column(Text, nullable=False)
    meta_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnomalyORM(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    detected_at = Column(DateTime, nullable=False, index=True)
    window_start = Column(DateTime, nullable=False)
    window_end = Column(DateTime, nullable=False)
    severity = Column(String(50), nullable=False)
    details = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertConfigORM(Base):
    __tablename__ = "alert_configs"

    id = Column(Integer, primary_key=True, index=True)
    webhook_url = Column(String(512), nullable=False)
    event_types = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class AlertHistoryORM(Base):
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(Integer, ForeignKey("anomalies.id"), nullable=False)
    config_id = Column(Integer, ForeignKey("alert_configs.id"), nullable=False)
    status = Column(String(50), nullable=False)
    sent_at = Column(DateTime, nullable=True)
    response_status = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
