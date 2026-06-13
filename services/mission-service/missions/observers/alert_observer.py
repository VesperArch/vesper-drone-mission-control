"""
DESIGN PATTERN: Observer — Concrete Observer #2
────────────────────────────────────────────────
AlertObserver reacts to high-severity events by persisting an alert record and
producing a visible console warning. In a production system this would dispatch
SMS/push notifications — swapped in transparently without touching the subject.
"""

from loguru import logger
from core.events import MissionObserverInterface, MissionEventData

# Events that require an operator alert
_ALERT_EVENTS = {"LOW_BATTERY", "BAD_WEATHER", "SIGNAL_LOST", "MISSION_FAILED", "OBSTACLE_DETECTED"}


class AlertObserver(MissionObserverInterface):
    """
    Filters mission events and raises operator alerts for critical conditions.
    Maintains a local alert buffer accessible via get_alerts().
    """

    def __init__(self) -> None:
        self._alerts: list[dict] = []

    def update(self, event: MissionEventData) -> None:
        if event.event_type not in _ALERT_EVENTS:
            return

        alert = {
            "mission_id": event.mission_id,
            "event_type": event.event_type,
            "message": event.message,
            "timestamp": event.timestamp.isoformat(),
            "severity": event.severity,
        }
        self._alerts.append(alert)
        logger.warning(f"⚠  OPERATOR ALERT [{event.event_type}] — {event.message}")

    def get_alerts(self) -> list[dict]:
        return list(self._alerts)

    def clear(self) -> None:
        self._alerts.clear()
