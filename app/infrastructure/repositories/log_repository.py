from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import LogEntry
from app.domain.interfaces import LogRepository
from app.infrastructure.database import LogEntryORM


class SQLLogRepository(LogRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, entry: LogEntry) -> LogEntry:
        orm = LogEntryORM(
            timestamp=entry.timestamp,
            service=entry.service,
            level=entry.level.value,
            message=entry.message,
            meta_data=entry.meta_data,
        )
        self._session.add(orm)
        await self._session.flush()
        await self._session.refresh(orm)
        return LogEntry.model_validate(orm)

    async def save_many(self, entries: List[LogEntry]) -> List[LogEntry]:
        orms = [
            LogEntryORM(
                timestamp=e.timestamp,
                service=e.service,
                level=e.level.value,
                message=e.message,
                meta_data=e.meta_data,
            )
            for e in entries
        ]
        self._session.add_all(orms)
        await self._session.flush()
        return [LogEntry.model_validate(o) for o in orms]

    async def get_by_window(
        self, start: datetime, end: datetime, service: Optional[str] = None
    ) -> List[LogEntry]:
        stmt = select(LogEntryORM).where(
            LogEntryORM.timestamp >= start, LogEntryORM.timestamp <= end
        )
        if service:
            stmt = stmt.where(LogEntryORM.service == service)
        result = await self._session.execute(stmt)
        return [LogEntry.model_validate(r) for r in result.scalars().all()]

    async def get_recent(self, limit: int = 100) -> List[LogEntry]:
        stmt = select(LogEntryORM).order_by(desc(LogEntryORM.timestamp)).limit(limit)
        result = await self._session.execute(stmt)
        return [LogEntry.model_validate(r) for r in result.scalars().all()]
