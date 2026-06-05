import json
import re
from datetime import datetime
from typing import Dict, Any, List
from app.domain.models import LogEntry, LogLevel
from app.core.exceptions import ParseException


class LogParser:
    """Robust multi-format log parser with pluggable rules."""

    def parse(self, raw: str, source_format: str = "auto") -> LogEntry:
        if source_format == "json":
            return self._parse_json(raw)
        if source_format == "syslog":
            return self._parse_syslog(raw)
        if source_format == "auto":
            try:
                return self._parse_json(raw)
            except Exception:
                return self._parse_syslog(raw)
        raise ParseException(f"Unsupported format: {source_format}")

    def parse_batch(self, raw_lines: List[str], source_format: str = "auto") -> List[LogEntry]:
        entries = []
        errors = []
        for line in raw_lines:
            try:
                entries.append(self.parse(line, source_format))
            except Exception as exc:
                errors.append({"line": line, "error": str(exc)})
        if errors:
            # Log errors but don't fail entire batch
            raise ParseException(f"Partial batch failure: {len(errors)} lines failed")
        return entries

    def _parse_json(self, raw: str) -> LogEntry:
        try:
            data: Dict[str, Any] = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ParseException("Invalid JSON") from exc

        timestamp = self._extract_timestamp(data)
        level = self._extract_level(data)
        service = data.get("service", data.get("source", "unknown"))
        message = data.get("message", data.get("msg", ""))
        meta_data = {k: v for k, v in data.items() if k not in ("timestamp", "level", "service", "source", "message", "msg")}
        return LogEntry(
            timestamp=timestamp,
            service=str(service),
            level=level,
            message=str(message),
            meta_data=meta_data,
        )

    def _parse_syslog(self, raw: str) -> LogEntry:
        # Simple syslog regex: <priority>timestamp host service[pid]: message
        pattern = r"^(?:<\d+>)?(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+([^\s\[]+)(?:\[\d+\])?:\s+(.*)$"
        match = re.match(pattern, raw)
        if not match:
            # Fallback: treat entire line as message with current time
            return LogEntry(
                timestamp=datetime.utcnow(),
                service="unknown",
                level=LogLevel.INFO,
                message=raw,
                metadata={},
            )
        ts_str, host, service, message = match.groups()
        # Use current year since syslog lacks it
        current_year = datetime.utcnow().year
        try:
            timestamp = datetime.strptime(f"{current_year} {ts_str}", "%Y %b %d %H:%M:%S")
        except ValueError:
            timestamp = datetime.utcnow()
        level = self._infer_level(message)
        return LogEntry(
            timestamp=timestamp,
            service=service,
            level=level,
            message=message,
            metadata={"host": host},
        )

    @staticmethod
    def _extract_timestamp(data: Dict[str, Any]) -> datetime:
        ts = data.get("timestamp", data.get("time", data.get("ts")))
        if isinstance(ts, datetime):
            return ts
        if isinstance(ts, str):
            for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
                try:
                    return datetime.strptime(ts, fmt)
                except ValueError:
                    continue
        return datetime.utcnow()

    @staticmethod
    def _extract_level(data: Dict[str, Any]) -> LogLevel:
        lvl = str(data.get("level", data.get("severity", "INFO"))).upper()
        try:
            return LogLevel(lvl)
        except ValueError:
            return LogLevel.INFO

    @staticmethod
    def _infer_level(message: str) -> LogLevel:
        msg_upper = message.upper()
        for lvl in (LogLevel.CRITICAL, LogLevel.ERROR, LogLevel.WARNING, LogLevel.DEBUG):
            if lvl.value in msg_upper:
                return lvl
        return LogLevel.INFO
