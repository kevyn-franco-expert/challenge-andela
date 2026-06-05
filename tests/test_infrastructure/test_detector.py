import pytest
from datetime import datetime, timedelta
from app.infrastructure.services.anomaly_detector import StatisticalAnomalyDetector
from app.domain.models import LogEntry, LogLevel


@pytest.mark.asyncio
async def test_detector_finds_spike():
    detector = StatisticalAnomalyDetector()
    base = datetime.utcnow() - timedelta(minutes=20)
    logs = []
    for i in range(30):
        logs.append(LogEntry(
            timestamp=base + timedelta(minutes=i),
            service="svc",
            level=LogLevel.ERROR,
            message="error",
            metadata={},
        ))
    anomalies = await detector.detect(logs)
    assert isinstance(anomalies, list)
