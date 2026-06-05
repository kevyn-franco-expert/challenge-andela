from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import app.infrastructure.database as db_module
from app.infrastructure.repositories.log_repository import SQLLogRepository
from app.infrastructure.repositories.anomaly_repository import SQLAnomalyRepository
from app.infrastructure.repositories.alert_repository import SQLAlertRepository
from app.infrastructure.services.log_parser import LogParser
from app.infrastructure.services.anomaly_detector import StatisticalAnomalyDetector
from app.infrastructure.services.webhook_dispatcher import HTTPWebhookDispatcher
from app.application.use_cases.ingest_logs import IngestLogsUseCase
from app.application.use_cases.detect_anomalies import DetectAnomaliesUseCase
from app.application.use_cases.trigger_alerts import TriggerAlertsUseCase


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_module.AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_log_repo(session: AsyncSession) -> SQLLogRepository:
    return SQLLogRepository(session)


def get_anomaly_repo(session: AsyncSession) -> SQLAnomalyRepository:
    return SQLAnomalyRepository(session)


def get_alert_repo(session: AsyncSession) -> SQLAlertRepository:
    return SQLAlertRepository(session)


def get_parser() -> LogParser:
    return LogParser()


def get_detector() -> StatisticalAnomalyDetector:
    return StatisticalAnomalyDetector()


def get_dispatcher() -> HTTPWebhookDispatcher:
    return HTTPWebhookDispatcher()


def get_ingest_use_case(session: AsyncSession) -> IngestLogsUseCase:
    return IngestLogsUseCase(get_log_repo(session), get_parser())


def get_detect_use_case(session: AsyncSession) -> DetectAnomaliesUseCase:
    return DetectAnomaliesUseCase(
        get_log_repo(session),
        get_anomaly_repo(session),
        get_detector(),
    )


def get_alert_use_case(session: AsyncSession) -> TriggerAlertsUseCase:
    return TriggerAlertsUseCase(
        get_alert_repo(session),
        get_anomaly_repo(session),
        get_dispatcher(),
    )
