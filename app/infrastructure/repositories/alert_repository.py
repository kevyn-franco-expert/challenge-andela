from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import AlertConfig, AlertHistory
from app.domain.interfaces import AlertRepository
from app.infrastructure.database import AlertConfigORM, AlertHistoryORM


class SQLAlertRepository(AlertRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save_config(self, config: AlertConfig) -> AlertConfig:
        orm = AlertConfigORM(
            webhook_url=config.webhook_url,
            event_types=config.event_types,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return AlertConfig.model_validate(orm)

    async def get_configs(self) -> List[AlertConfig]:
        stmt = select(AlertConfigORM)
        result = await self._session.execute(stmt)
        return [AlertConfig.model_validate(r) for r in result.scalars().all()]

    async def save_history(self, history: AlertHistory) -> AlertHistory:
        orm = AlertHistoryORM(
            anomaly_id=history.anomaly_id,
            config_id=history.config_id,
            status=history.status,
            sent_at=history.sent_at,
            response_status=history.response_status,
            error_message=history.error_message,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return AlertHistory.model_validate(orm)

    async def get_history(self, limit: int = 100) -> List[AlertHistory]:
        stmt = select(AlertHistoryORM).order_by(desc(AlertHistoryORM.created_at)).limit(limit)
        result = await self._session.execute(stmt)
        return [AlertHistory.model_validate(r) for r in result.scalars().all()]
