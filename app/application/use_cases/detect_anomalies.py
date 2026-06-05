import logging
from datetime import datetime, timedelta
from typing import List
from app.domain.models import Anomaly
from app.domain.interfaces import LogRepository, AnomalyRepository, AnomalyDetector
from app.core.config import settings

logger = logging.getLogger(__name__)


class DetectAnomaliesUseCase:
    def __init__(
        self,
        log_repo: LogRepository,
        anomaly_repo: AnomalyRepository,
        detector: AnomalyDetector,
    ):
        self._log_repo = log_repo
        self._anomaly_repo = anomaly_repo
        self._detector = detector

    async def execute(self, window_minutes: int = None) -> List[Anomaly]:
        window = window_minutes or settings.anomaly_window_minutes
        end = datetime.utcnow()
        start = end - timedelta(minutes=window * 10)  # Look back 10x the window for context

        logs = await self._log_repo.get_by_window(start, end)
        if not logs:
            logger.info("No logs found for anomaly detection window")
            return []

        anomalies = await self._detector.detect(logs)
        saved = []
        for anomaly in anomalies:
            existing = await self._anomaly_repo.get_recent(limit=100)
            # Simple dedup: if same window and details prefix exists in last 100, skip
            if not any(
                a.window_start == anomaly.window_start
                and a.window_end == anomaly.window_end
                and a.details[:80] == anomaly.details[:80]
                for a in existing
            ):
                saved.append(await self._anomaly_repo.save(anomaly))
            else:
                logger.info("Duplicate anomaly suppressed", extra={"details": anomaly.details[:100]})

        logger.info("Anomaly detection complete", extra={"detected": len(anomalies), "saved": len(saved)})
        return saved
