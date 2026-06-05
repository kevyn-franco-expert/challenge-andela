from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    service: str
    level: LogLevel
    message: str
    meta_data: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class Anomaly(BaseModel):
    id: Optional[int] = None
    detected_at: datetime
    window_start: datetime
    window_end: datetime
    severity: Severity
    details: str
    status: AnomalyStatus = AnomalyStatus.OPEN
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AlertConfig(BaseModel):
    id: Optional[int] = None
    webhook_url: str
    event_types: list[str] = Field(default_factory=lambda: ["ANOMALY"])
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AlertHistory(BaseModel):
    id: Optional[int] = None
    anomaly_id: int
    config_id: int
    status: str  # PENDING, SENT, FAILED
    sent_at: Optional[datetime] = None
    response_status: Optional[int] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
