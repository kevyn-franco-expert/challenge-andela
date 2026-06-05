from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.api.dependencies import get_db, get_alert_use_case, get_alert_repo
from app.application.use_cases.trigger_alerts import TriggerAlertsUseCase
from app.application.dto.alert_dto import AlertConfigRequest, AlertConfigResponse, AlertHistoryResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/configs", response_model=AlertConfigResponse)
async def create_alert_config(
    request: AlertConfigRequest,
    session: AsyncSession = Depends(get_db),
) -> AlertConfigResponse:
    repo = get_alert_repo(session)
    from app.domain.models import AlertConfig
    config = AlertConfig(webhook_url=request.webhook_url, event_types=request.event_types)
    saved = await repo.save_config(config)
    return AlertConfigResponse.model_validate(saved)


@router.get("/configs", response_model=List[AlertConfigResponse])
async def list_alert_configs(
    session: AsyncSession = Depends(get_db),
) -> List[AlertConfigResponse]:
    repo = get_alert_repo(session)
    configs = await repo.get_configs()
    return [AlertConfigResponse.model_validate(c) for c in configs]


@router.post("/trigger")
async def trigger_alerts(
    session: AsyncSession = Depends(get_db),
) -> dict:
    uc = get_alert_use_case(session)
    history = await uc.execute()
    return {"triggered": len(history)}


@router.get("/history", response_model=List[AlertHistoryResponse])
async def alert_history(
    limit: int = 100,
    session: AsyncSession = Depends(get_db),
) -> List[AlertHistoryResponse]:
    repo = get_alert_repo(session)
    history = await repo.get_history(limit=limit)
    return [AlertHistoryResponse.model_validate(h) for h in history]
