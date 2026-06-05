import asyncio
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List
from app.domain.models import LogEntry, Anomaly, Severity, LogLevel
from app.core.config import settings
from app.core.exceptions import DetectionException


class StatisticalAnomalyDetector:
    """
    Hybrid unsupervised anomaly detector (no external ML libs):
    1. Z-score spike detection on error counts per service / time window.
    2. Centroid-distance multivariate outlier detection on log features.
    """

    def __init__(self):
        self._z_threshold = settings.anomaly_threshold_zscore
        self._window_minutes = settings.anomaly_window_minutes

    async def detect(self, logs: List[LogEntry]) -> List[Anomaly]:
        if not logs:
            return []
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._detect_sync, logs)

    def _detect_sync(self, logs: List[LogEntry]) -> List[Anomaly]:
        try:
            anomalies = []
            anomalies.extend(self._detect_spikes(logs))
            anomalies.extend(self._detect_multivariate(logs))
            return self._deduplicate(anomalies)
        except Exception as exc:
            raise DetectionException("Detection pipeline failed") from exc

    def _detect_spikes(self, logs: List[LogEntry]) -> List[Anomaly]:
        windows = defaultdict(lambda: defaultdict(int))  # service -> window -> error_count
        for log in logs:
            window = self._floor_window(log.timestamp)
            is_error = log.level in (LogLevel.ERROR, LogLevel.CRITICAL)
            windows[log.service][window] += 1 if is_error else 0

        results = []
        for service, window_counts in windows.items():
            if len(window_counts) < 3:
                continue
            counts = list(window_counts.values())
            try:
                mean_err = statistics.mean(counts)
                std_err = statistics.stdev(counts)
            except statistics.StatisticsError:
                continue
            if std_err == 0:
                continue
            for window, count in window_counts.items():
                zscore = (count - mean_err) / std_err
                if zscore >= self._z_threshold:
                    window_end = window + timedelta(minutes=self._window_minutes)
                    severity = Severity.CRITICAL if zscore >= 3.0 else Severity.HIGH
                    details = (
                        f"Service '{service}' error spike. "
                        f"Errors={int(count)} mean={mean_err:.1f} std={std_err:.1f} z={zscore:.2f}"
                    )
                    results.append(Anomaly(
                        detected_at=datetime.utcnow(),
                        window_start=window,
                        window_end=window_end,
                        severity=severity,
                        details=details,
                    ))
        return results

    def _detect_multivariate(self, logs: List[LogEntry]) -> List[Anomaly]:
        if len(logs) < 10:
            return []

        # Feature vector per log
        features = []
        for log in logs:
            features.append({
                "hour": log.timestamp.hour,
                "minute": log.timestamp.minute,
                "is_error": 1 if log.level in (LogLevel.ERROR, LogLevel.CRITICAL) else 0,
                "msg_len": len(log.message),
                "service": log.service,
                "timestamp": log.timestamp,
            })

        n = len(features)
        centroid = {
            "hour": sum(f["hour"] for f in features) / n,
            "minute": sum(f["minute"] for f in features) / n,
            "is_error": sum(f["is_error"] for f in features) / n,
            "msg_len": sum(f["msg_len"] for f in features) / n,
        }

        max_msg_len = max((f["msg_len"] for f in features), default=1) or 1

        distances = []
        for f in features:
            d = (
                ((f["hour"] - centroid["hour"]) / 23) ** 2 +
                ((f["minute"] - centroid["minute"]) / 59) ** 2 +
                ((f["is_error"] - centroid["is_error"]) / 1) ** 2 +
                ((f["msg_len"] - centroid["msg_len"]) / max_msg_len) ** 2
            ) ** 0.5
            distances.append(d)

        try:
            mean_dist = statistics.mean(distances)
            std_dist = statistics.stdev(distances)
        except statistics.StatisticsError:
            return []

        threshold = mean_dist + 2 * std_dist
        outliers = [features[i] for i, d in enumerate(distances) if d > threshold and features[i]["is_error"] == 1]
        if not outliers:
            return []

        # Group by service+hour, require at least 2 outlier logs to raise anomaly
        groups = defaultdict(int)
        for o in outliers:
            groups[(o["service"], o["hour"])] += 1

        results = []
        for (service, hour), count in groups.items():
            if count < 2:
                continue
            base_day = min((o["timestamp"] for o in outliers if o["service"] == service and o["hour"] == hour), default=datetime.utcnow())
            hour_start = base_day.replace(hour=hour, minute=0, second=0, microsecond=0)
            hour_end = hour_start + timedelta(hours=1)
            details = (
                f"Multivariate anomaly for '{service}'. "
                f"Outlier error logs in hour {hour}: {count} (dist_threshold={threshold:.2f})"
            )
            results.append(Anomaly(
                detected_at=datetime.utcnow(),
                window_start=hour_start,
                window_end=hour_end,
                severity=Severity.MEDIUM,
                details=details,
            ))
        return results

    def _floor_window(self, ts: datetime) -> datetime:
        minute = (ts.minute // self._window_minutes) * self._window_minutes
        return ts.replace(minute=minute, second=0, microsecond=0)

    @staticmethod
    def _deduplicate(anomalies: List[Anomaly]) -> List[Anomaly]:
        seen = set()
        deduped = []
        for a in anomalies:
            key = (a.window_start, a.window_end, a.details[:120])
            if key not in seen:
                seen.add(key)
                deduped.append(a)
        return deduped
