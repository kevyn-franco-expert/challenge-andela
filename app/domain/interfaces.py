from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from app.domain.models import LogEntry, Anomaly, AlertConfig, AlertHistory


class LogRepository(ABC):
    @abstractmethod
    async def save(self, entry: LogEntry) -> LogEntry:
        raise NotImplementedError

    @abstractmethod
    async def save_many(self, entries: List[LogEntry]) -> List[LogEntry]:
        raise NotImplementedError

    @abstractmethod
    async def get_by_window(
        self, start: datetime, end: datetime, service: Optional[str] = None
    ) -> List[LogEntry]:
        raise NotImplementedError

    @abstractmethod
    async def get_recent(self, limit: int = 100) -> List[LogEntry]:
        raise NotImplementedError


class AnomalyRepository(ABC):
    @abstractmethod
    async def save(self, anomaly: Anomaly) -> Anomaly:
        raise NotImplementedError

    @abstractmethod
    async def get_open(self) -> List[Anomaly]:
        raise NotImplementedError

    @abstractmethod
    async def get_recent(self, limit: int = 50) -> List[Anomaly]:
        raise NotImplementedError


class AlertRepository(ABC):
    @abstractmethod
    async def save_config(self, config: AlertConfig) -> AlertConfig:
        raise NotImplementedError

    @abstractmethod
    async def get_configs(self) -> List[AlertConfig]:
        raise NotImplementedError

    @abstractmethod
    async def save_history(self, history: AlertHistory) -> AlertHistory:
        raise NotImplementedError

    @abstractmethod
    async def get_history(self, limit: int = 100) -> List[AlertHistory]:
        raise NotImplementedError


class AnomalyDetector(ABC):
    @abstractmethod
    async def detect(self, logs: List[LogEntry]) -> List[Anomaly]:
        raise NotImplementedError


class WebhookDispatcher(ABC):
    @abstractmethod
    async def dispatch(self, webhook_url: str, payload: dict) -> dict:
        raise NotImplementedError
