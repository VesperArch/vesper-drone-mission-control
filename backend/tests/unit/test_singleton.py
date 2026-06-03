import pytest
from datetime import datetime

from core.singleton.mission_control_center import (
    MissionControlCenter,
    DroneRecord,
    MissionRecord,
    EventRecord,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the Singleton before each test to isolate state."""
    MissionControlCenter._instance = None
    MissionControlCenter._initialized = False
    yield
    MissionControlCenter._instance = None
    MissionControlCenter._initialized = False


def make_drone(drone_id: str = "drone-1") -> DroneRecord:
    return DroneRecord(
        drone_id=drone_id,
        drone_name="Sentinel Alpha",
        drone_type="SURVEILLANCE",
        status="IDLE",
        battery_level=100.0,
    )


def make_mission(mission_id: str = "mission-1") -> MissionRecord:
    return MissionRecord(
        mission_id=mission_id,
        mission_type="FLOOD_MONITORING",
        region="Itaipuaçu",
        drone_id="drone-1",
        strategy="FASTEST",
        status="ACTIVE",
    )


class TestSingletonInstance:
    def test_get_instance_returns_same_object(self):
        a = MissionControlCenter.get_instance()
        b = MissionControlCenter.get_instance()
        assert a is b

    def test_direct_instantiation_returns_same_object(self):
        instance = MissionControlCenter.get_instance()
        direct = MissionControlCenter()
        assert instance is direct

    def test_instance_is_mission_control_center(self):
        assert isinstance(MissionControlCenter.get_instance(), MissionControlCenter)


class TestDroneRegistry:
    def test_register_and_get_drone(self):
        cc = MissionControlCenter.get_instance()
        drone = make_drone("d-1")
        cc.register_drone(drone)
        assert cc.get_drone("d-1") is drone

    def test_get_unknown_drone_returns_none(self):
        cc = MissionControlCenter.get_instance()
        assert cc.get_drone("nonexistent") is None

    def test_list_drones_includes_registered(self):
        cc = MissionControlCenter.get_instance()
        cc.register_drone(make_drone("d-1"))
        cc.register_drone(make_drone("d-2"))
        ids = [d.drone_id for d in cc.list_drones()]
        assert "d-1" in ids
        assert "d-2" in ids

    def test_update_drone_status(self):
        cc = MissionControlCenter.get_instance()
        cc.register_drone(make_drone("d-1"))
        cc.update_drone_status("d-1", "ACTIVE")
        assert cc.get_drone("d-1").status == "ACTIVE"

    def test_update_drone_battery(self):
        cc = MissionControlCenter.get_instance()
        cc.register_drone(make_drone("d-1"))
        cc.update_drone_status("d-1", "ACTIVE", battery_level=55.0)
        assert cc.get_drone("d-1").battery_level == 55.0

    def test_update_unknown_drone_is_silent(self):
        cc = MissionControlCenter.get_instance()
        cc.update_drone_status("nonexistent", "ACTIVE")  # should not raise


class TestMissionTracking:
    def test_register_and_get_mission(self):
        cc = MissionControlCenter.get_instance()
        mission = make_mission("m-1")
        cc.register_mission(mission)
        assert cc.get_mission("m-1") is mission

    def test_get_unknown_mission_returns_none(self):
        cc = MissionControlCenter.get_instance()
        assert cc.get_mission("nonexistent") is None

    def test_register_increments_total_missions(self):
        cc = MissionControlCenter.get_instance()
        cc.register_mission(make_mission("m-1"))
        cc.register_mission(make_mission("m-2"))
        assert cc.get_statistics()["total_missions"] == 2

    def test_update_mission_status(self):
        cc = MissionControlCenter.get_instance()
        cc.register_mission(make_mission("m-1"))
        cc.update_mission_status("m-1", "COMPLETED")
        assert cc.get_mission("m-1").status == "COMPLETED"

    def test_update_unknown_mission_is_silent(self):
        cc = MissionControlCenter.get_instance()
        cc.update_mission_status("nonexistent", "COMPLETED")  # should not raise

    def test_list_missions_includes_registered(self):
        cc = MissionControlCenter.get_instance()
        cc.register_mission(make_mission("m-1"))
        ids = [m.mission_id for m in cc.list_missions()]
        assert "m-1" in ids


class TestEventLog:
    def test_log_event_and_retrieve(self):
        cc = MissionControlCenter.get_instance()
        event = EventRecord(mission_id="m-1", event_type="MISSION_STARTED", message="Started")
        cc.log_event(event)
        log = cc.get_event_log()
        assert len(log) == 1
        assert log[0].event_type == "MISSION_STARTED"

    def test_event_log_is_reverse_chronological(self):
        cc = MissionControlCenter.get_instance()
        cc.log_event(EventRecord(mission_id="m-1", event_type="FIRST", message="First"))
        cc.log_event(EventRecord(mission_id="m-1", event_type="SECOND", message="Second"))
        log = cc.get_event_log()
        assert log[0].event_type == "SECOND"
        assert log[1].event_type == "FIRST"

    def test_log_event_increments_total_events(self):
        cc = MissionControlCenter.get_instance()
        cc.log_event(EventRecord(mission_id="m-1", event_type="X", message=""))
        cc.log_event(EventRecord(mission_id="m-1", event_type="Y", message=""))
        assert cc.get_statistics()["total_events_fired"] == 2


class TestStatistics:
    def test_statistics_keys_present(self):
        cc = MissionControlCenter.get_instance()
        stats = cc.get_statistics()
        for key in ["total_missions", "active_missions", "completed_missions",
                    "total_drones", "idle_drones", "active_drones", "total_events_fired"]:
            assert key in stats

    def test_active_missions_count(self):
        cc = MissionControlCenter.get_instance()
        m1 = make_mission("m-1")
        m1.status = "ACTIVE"
        m2 = make_mission("m-2")
        m2.status = "COMPLETED"
        cc.register_mission(m1)
        cc.register_mission(m2)
        assert cc.get_statistics()["active_missions"] == 1
        assert cc.get_statistics()["completed_missions"] == 1

    def test_idle_and_active_drone_counts(self):
        cc = MissionControlCenter.get_instance()
        d1 = make_drone("d-1")
        d2 = make_drone("d-2")
        d2.status = "ACTIVE"
        cc.register_drone(d1)
        cc.register_drone(d2)
        assert cc.get_statistics()["idle_drones"] == 1
        assert cc.get_statistics()["active_drones"] == 1
