import pytest
from datetime import datetime
from app.infrastructure.services.log_parser import LogParser
from app.domain.models import LogLevel


@pytest.mark.asyncio
async def test_parse_json():
    parser = LogParser()
    raw = '{"timestamp": "2024-06-01T10:00:00Z", "service": "test", "level": "WARNING", "message": "low disk"}'
    entry = parser.parse(raw, "json")
    assert entry.service == "test"
    assert entry.level == LogLevel.WARNING
    assert entry.message == "low disk"


@pytest.mark.asyncio
async def test_parse_syslog():
    parser = LogParser()
    raw = "Jun  1 10:00:00 host01 myapp[123]: ERROR disk full"
    entry = parser.parse(raw, "syslog")
    assert entry.service == "myapp"
    assert entry.level == LogLevel.ERROR
