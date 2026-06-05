import pytest


@pytest.mark.asyncio
async def test_create_alert_config(client):
    resp = await client.post("/alerts/configs", json={"webhook_url": "https://httpbin.org/post", "event_types": ["ANOMALY"]})
    assert resp.status_code == 200
    data = resp.json()
    assert data["webhook_url"] == "https://httpbin.org/post"


@pytest.mark.asyncio
async def test_list_alert_configs(client):
    await client.post("/alerts/configs", json={"webhook_url": "https://example.com/hook", "event_types": ["ANOMALY"]})
    resp = await client.get("/alerts/configs")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_trigger_alerts(client):
    resp = await client.post("/alerts/trigger")
    assert resp.status_code == 200
    data = resp.json()
    assert "triggered" in data
