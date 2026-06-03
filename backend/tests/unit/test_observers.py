import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.events.mission_events import MissionEventData
from missions.observers.alert_observer import AlertObserver
from missions.observers.logger_observer import LoggerObserver


def make_event(event_type: str, mission_id: str = "mission-001", severity: str = "INFO") -> MissionEventData:
    return MissionEventData(
        mission_id=mission_id,
        event_type=event_type,
        message=f"Test event: {event_type}",
        severity=severity,
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
    )


class TestLoggerObserver:
    def setup_method(self):
        self.observer = LoggerObserver()

    def test_update_does_not_raise(self):
        event = make_event("MISSION_STARTED", severity="INFO")
        self.observer.update(event)  # should not raise

    def test_accepts_all_event_types(self):
        for event_type in ["MISSION_STARTED", "MISSION_COMPLETED", "LOW_BATTERY", "MISSION_FAILED"]:
            event = make_event(event_type)
            self.observer.update(event)  # no exception


class TestAlertObserver:
    def setup_method(self):
        self.observer = AlertObserver()

    def test_buffer_starts_empty(self):
        assert self.observer.get_alerts() == []

    def test_alert_event_populates_buffer(self):
        self.observer.update(make_event("LOW_BATTERY", severity="WARNING"))
        assert len(self.observer.get_alerts()) == 1

    def test_bad_weather_triggers_alert(self):
        self.observer.update(make_event("BAD_WEATHER"))
        assert len(self.observer.get_alerts()) == 1

    def test_signal_lost_triggers_alert(self):
        self.observer.update(make_event("SIGNAL_LOST"))
        assert len(self.observer.get_alerts()) == 1

    def test_mission_failed_triggers_alert(self):
        self.observer.update(make_event("MISSION_FAILED"))
        assert len(self.observer.get_alerts()) == 1

    def test_obstacle_detected_triggers_alert(self):
        self.observer.update(make_event("OBSTACLE_DETECTED"))
        assert len(self.observer.get_alerts()) == 1

    def test_mission_started_does_not_trigger_alert(self):
        self.observer.update(make_event("MISSION_STARTED"))
        assert len(self.observer.get_alerts()) == 0

    def test_mission_completed_does_not_trigger_alert(self):
        self.observer.update(make_event("MISSION_COMPLETED"))
        assert len(self.observer.get_alerts()) == 0

    def test_return_to_base_does_not_trigger_alert(self):
        self.observer.update(make_event("RETURN_TO_BASE"))
        assert len(self.observer.get_alerts()) == 0

    def test_alert_contains_required_fields(self):
        self.observer.update(make_event("LOW_BATTERY", mission_id="m-42", severity="WARNING"))
        alert = self.observer.get_alerts()[0]
        assert alert["mission_id"] == "m-42"
        assert alert["event_type"] == "LOW_BATTERY"
        assert "message" in alert
        assert "timestamp" in alert
        assert "severity" in alert

    def test_get_alerts_returns_copy(self):
        self.observer.update(make_event("LOW_BATTERY"))
        alerts = self.observer.get_alerts()
        alerts.clear()
        assert len(self.observer.get_alerts()) == 1

    def test_clear_empties_buffer(self):
        self.observer.update(make_event("LOW_BATTERY"))
        self.observer.update(make_event("BAD_WEATHER"))
        self.observer.clear()
        assert self.observer.get_alerts() == []

    def test_multiple_alerts_accumulate(self):
        self.observer.update(make_event("LOW_BATTERY"))
        self.observer.update(make_event("BAD_WEATHER"))
        self.observer.update(make_event("SIGNAL_LOST"))
        assert len(self.observer.get_alerts()) == 3

    def test_alert_timestamp_is_iso_format(self):
        self.observer.update(make_event("LOW_BATTERY"))
        alert = self.observer.get_alerts()[0]
        # Should be parseable as ISO datetime
        datetime.fromisoformat(alert["timestamp"])
