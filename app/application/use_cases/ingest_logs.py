import logging
from typing import List
from app.domain.models import LogEntry
from app.domain.interfaces import LogRepository
from app.infrastructure.services.log_parser import LogParser
from app.core.exceptions import ParseException

logger = logging.getLogger(__name__)


class IngestLogsUseCase:
    def __init__(self, log_repo: LogRepository, parser: LogParser):
        self._repo = log_repo
        self._parser = parser

    async def execute(self, raw_lines: List[str], source_format: str = "auto") -> dict:
        entries: List[LogEntry] = []
        failed = 0
        for line in raw_lines:
            try:
                entry = self._parser.parse(line, source_format)
                entries.append(entry)
            except ParseException:
                failed += 1
                logger.warning("Failed to parse log line", extra={"line": line[:200]})
            except Exception:
                failed += 1
                logger.exception("Unexpected parse error")

        if entries:
            saved = await self._repo.save_many(entries)
            logger.info("Logs ingested", extra={"count": len(saved), "failed": failed})
            return {"ingested": len(saved), "failed": failed, "entries": saved}
        return {"ingested": 0, "failed": failed, "entries": []}
