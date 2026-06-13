"""
DESIGN PATTERN: Observer — Concrete Observer #1
────────────────────────────────────────────────
LoggerObserver subscribes to mission events and writes structured log entries
using loguru. It is completely unaware of AlertObserver or MissionStatusObserver.
"""

from loguru import logger
from core.events import MissionObserverInterface, MissionEventData


_SEVERITY_MAP = {
    "INFO": logger.info,
    "WARNING": logger.warning,
    "ALERT": logger.error,
    "SUCCESS": logger.success,
}


class LoggerObserver(MissionObserverInterface):
    """Writes every mission event to the application log."""

    def update(self, event: MissionEventData) -> None:
        log_fn = _SEVERITY_MAP.get(event.severity, logger.info)
        log_fn(
            f"[{event.event_type}] Mission {event.mission_id[:8]}… | {event.message}"
        )
