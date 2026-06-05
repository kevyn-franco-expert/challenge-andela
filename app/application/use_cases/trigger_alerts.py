import logging
from datetime import datetime
from typing import List
from app.domain.models import Anomaly, AlertHistory
from app.domain.interfaces import AnomalyRepository, AlertRepository, WebhookDispatcher
from app.infrastructure.services.webhook_dispatcher import HTTPWebhookDispatcher

logger = logging.getLogger(__name__)


class TriggerAlertsUseCase:
    def __init__(
        self,
        alert_repo: AlertRepository,
        anomaly_repo: AnomalyRepository,
        dispatcher: WebhookDispatcher,
    ):
        self._alert_repo = alert_repo
        self._anomaly_repo = anomaly_repo
        self._dispatcher = dispatcher

    async def execute(self, anomalies: List[Anomaly] = None) -> List[AlertHistory]:
        configs = await self._alert_repo.get_configs()
        if not configs:
            logger.info("No alert configs registered")
            return []

        if anomalies is None:
            anomalies = await self._anomaly_repo.get_open()

        results: List[AlertHistory] = []
        for anomaly in anomalies:
            for config in configs:
                history = AlertHistory(
                    anomaly_id=anomaly.id,
                    config_id=config.id,
                    status="PENDING",
                )
                history = await self._alert_repo.save_history(history)
                payload = {
                    "event": "ANOMALY",
                    "anomaly_id": anomaly.id,
                    "severity": anomaly.severity.value,
                    "details": anomaly.details,
                    "window_start": anomaly.window_start.isoformat(),
                    "window_end": anomaly.window_end.isoformat(),
                    "detected_at": anomaly.detected_at.isoformat(),
                }
                try:
                    dispatch_result = await self._dispatcher.dispatch(config.webhook_url, payload)
                    history.status = "SENT"
                    history.sent_at = datetime.utcnow()
                    history.response_status = dispatch_result.get("status_code")
                except Exception as exc:
                    logger.error("Alert dispatch failed", extra={"error": str(exc), "webhook": config.webhook_url})
                    history.status = "FAILED"
                    history.error_message = str(exc)[:500]
                history = await self._alert_repo.save_history(history)
                results.append(history)
        return results
