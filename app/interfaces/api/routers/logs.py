from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.api.dependencies import get_db, get_ingest_use_case, get_log_repo
from app.application.use_cases.ingest_logs import IngestLogsUseCase
from app.application.dto.log_dto import IngestLogRequest, IngestLogResponse, LogEntryResponse

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/ingest", response_model=IngestLogResponse)
async def ingest_logs(
    request: IngestLogRequest,
    session: AsyncSession = Depends(get_db),
) -> IngestLogResponse:
    uc = get_ingest_use_case(session)
    result = await uc.execute(request.raw_lines, request.source_format)
    return IngestLogResponse(**result)


@router.get("/recent", response_model=List[LogEntryResponse])
async def recent_logs(
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
) -> List[LogEntryResponse]:
    repo = get_log_repo(session)
    logs = await repo.get_recent(limit=limit)
    return [LogEntryResponse.model_validate(log) for log in logs]
