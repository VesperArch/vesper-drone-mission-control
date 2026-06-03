import pytest
from datetime import datetime
from pytest_bdd import scenarios, given, when, then, parsers

from core.events.mission_events import MissionEventData
from missions.observers.alert_observer import AlertObserver

scenarios("../../features/alert_observer.feature")

MISSION_ID = "bdd-mission-001"


@given("the alert observer is monitoring a mission", target_fixture="observer")
def observer():
    return AlertObserver()


@when("a LOW_BATTERY event occurs")
def low_battery_event(observer):
    observer.update(MissionEventData(
        mission_id=MISSION_ID,
        event_type="LOW_BATTERY",
        message="Battery below 25%",
        severity="WARNING",
        timestamp=datetime.now(),
    ))


@when("a BAD_WEATHER event occurs")
def bad_weather_event(observer):
    observer.update(MissionEventData(
        mission_id=MISSION_ID,
        event_type="BAD_WEATHER",
        message="Storm detected",
        severity="ALERT",
        timestamp=datetime.now(),
    ))


@when("a MISSION_STARTED event occurs")
def mission_started_event(observer):
    observer.update(MissionEventData(
        mission_id=MISSION_ID,
        event_type="MISSION_STARTED",
        message="Mission launched",
        severity="INFO",
        timestamp=datetime.now(),
    ))


@when("I clear the alert buffer")
def clear_buffer(observer):
    observer.clear()


@then(parsers.parse("the alert buffer should contain {count:d} alert"))
def check_alert_count(observer, count):
    assert len(observer.get_alerts()) == count


@then("the alert buffer should be empty")
def check_buffer_empty(observer):
    assert observer.get_alerts() == []


@then("the alert should reference the correct mission")
def check_mission_reference(observer):
    alerts = observer.get_alerts()
    assert len(alerts) > 0
    assert alerts[0]["mission_id"] == MISSION_ID
