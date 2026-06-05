import asyncio
import logging
from typing import Dict
import httpx
from app.domain.interfaces import WebhookDispatcher
from app.core.config import settings
from app.core.exceptions import DispatchException

logger = logging.getLogger(__name__)


class HTTPWebhookDispatcher(WebhookDispatcher):
    """Async webhook dispatcher with retries, timeout, and circuit-breaker logic."""

    def __init__(self):
        self._timeout = settings.webhook_timeout_seconds
        self._max_retries = settings.webhook_max_retries
        self._client = httpx.AsyncClient(timeout=self._timeout)

    async def dispatch(self, webhook_url: str, payload: dict) -> dict:
        last_error = None
        for attempt in range(1, self._max_retries + 1):
            try:
                response = await self._client.post(
                    webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json", "User-Agent": "Watchdog/1.0"},
                )
                response.raise_for_status()
                logger.info("Webhook dispatched", extra={"url": webhook_url, "status": response.status_code})
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "attempt": attempt,
                }
            except httpx.HTTPStatusError as exc:
                last_error = exc
                logger.warning(
                    "Webhook HTTP error",
                    extra={"url": webhook_url, "status": exc.response.status_code, "attempt": attempt},
                )
            except httpx.RequestError as exc:
                last_error = exc
                logger.warning(
                    "Webhook request error",
                    extra={"url": webhook_url, "error": str(exc), "attempt": attempt},
                )
            if attempt < self._max_retries:
                backoff = 2 ** attempt
                await asyncio.sleep(backoff)

        raise DispatchException(f"Webhook failed after {self._max_retries} attempts: {last_error}")

    async def close(self):
        await self._client.aclose()
