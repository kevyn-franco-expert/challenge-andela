from typing import List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import Anomaly
from app.domain.interfaces import AnomalyRepository
from app.infrastructure.database import AnomalyORM


class SQLAnomalyRepository(AnomalyRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, anomaly: Anomaly) -> Anomaly:
        orm = AnomalyORM(
            detected_at=anomaly.detected_at,
            window_start=anomaly.window_start,
            window_end=anomaly.window_end,
            severity=anomaly.severity.value,
            details=anomaly.details,
            status=anomaly.status.value,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return Anomaly.model_validate(orm)

    async def get_open(self) -> List[Anomaly]:
        stmt = select(AnomalyORM).where(AnomalyORM.status == "OPEN").order_by(desc(AnomalyORM.detected_at))
        result = await self._session.execute(stmt)
        return [Anomaly.model_validate(r) for r in result.scalars().all()]

    async def get_recent(self, limit: int = 50) -> List[Anomaly]:
        stmt = select(AnomalyORM).order_by(desc(AnomalyORM.detected_at)).limit(limit)
        result = await self._session.execute(stmt)
        return [Anomaly.model_validate(r) for r in result.scalars().all()]
