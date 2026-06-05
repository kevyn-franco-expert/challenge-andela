import pytest


@pytest.mark.asyncio
async def test_ingest_json_logs(client):
    lines = [
        '{"timestamp": "2024-01-01T12:00:00Z", "service": "api", "level": "ERROR", "message": "DB timeout"}',
        '{"timestamp": "2024-01-01T12:01:00Z", "service": "api", "level": "ERROR", "message": "DB timeout 2"}',
    ]
    resp = await client.post("/logs/ingest", json={"raw_lines": lines, "source_format": "json"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ingested"] == 2
    assert data["failed"] == 0


@pytest.mark.asyncio
async def test_ingest_syslog(client):
    lines = [
        "Jan  1 12:00:00 host01 app[123]: ERROR connection refused",
    ]
    resp = await client.post("/logs/ingest", json={"raw_lines": lines, "source_format": "syslog"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["ingested"] == 1
