from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from app.domain.models import LogLevel


class IngestLogRequest(BaseModel):
    raw_lines: List[str]
    source_format: str = Field(default="auto", pattern="^(auto|json|syslog)$")


class LogEntryResponse(BaseModel):
    id: int
    timestamp: datetime
    service: str
    level: LogLevel
    message: str
    meta_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class IngestLogResponse(BaseModel):
    ingested: int
    failed: int
    entries: List[LogEntryResponse]
