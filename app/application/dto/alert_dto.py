from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class AlertConfigRequest(BaseModel):
    webhook_url: str = Field(..., min_length=1)
    event_types: list[str] = Field(default_factory=lambda: ["ANOMALY"])


class AlertConfigResponse(BaseModel):
    id: int
    webhook_url: str
    event_types: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertHistoryResponse(BaseModel):
    id: int
    anomaly_id: int
    config_id: int
    status: str
    sent_at: Optional[datetime]
    response_status: Optional[int]
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
