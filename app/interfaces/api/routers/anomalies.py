from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.api.dependencies import get_db, get_detect_use_case
from app.application.use_cases.detect_anomalies import DetectAnomaliesUseCase
from app.domain.models import Anomaly

router = APIRouter(prefix="/anomalies", tags=["anomalies"])


@router.post("/detect", response_model=List[Anomaly])
async def detect_anomalies(
    session: AsyncSession = Depends(get_db),
) -> List[Anomaly]:
    uc = get_detect_use_case(session)
    return await uc.execute()


@router.get("/recent", response_model=List[Anomaly])
async def recent_anomalies(
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
) -> List[Anomaly]:
    from app.interfaces.api.dependencies import get_anomaly_repo
    repo = get_anomaly_repo(session)
    return await repo.get_recent(limit=limit)
