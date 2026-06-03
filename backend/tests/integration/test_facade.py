import pytest
import uuid
from unittest.mock import patch

from core.facade.drone_mission_facade import DroneMissionFacade
from core.singleton.mission_control_center import MissionControlCenter
from core.enums import MissionStatus, DroneStatus, MissionType, MaricaRegion, RouteStrategyType, MissionPriority


@pytest.fixture(autouse=True)
def reset_singleton():
    MissionControlCenter._instance = None
    MissionControlCenter._initialized = False
    yield
    MissionControlCenter._instance = None
    MissionControlCenter._initialized = False


@pytest.fixture
def facade():
    return DroneMissionFacade()


@pytest.mark.django_db
class TestCreateAndStartMission:
    def test_returns_dict_with_id(self, facade, idle_drone):
        with patch("threading.Thread.start"):
            result = facade.create_and_start_mission({
                "drone_id": str(idle_drone.id),
                "mission_type": MissionType.FLOOD_MONITORING,
                "region": MaricaRegion.ITAIPUACU,
                "route_strategy": RouteStrategyType.FASTEST,
                "priority": MissionPriority.MEDIUM,
                "name": "Test Mission",
            })
        assert "id" in result

    def test_mission_status_is_active(self, facade, idle_drone):
        with patch("threading.Thread.start"):
            result = facade.create_and_start_mission({
                "drone_id": str(idle_drone.id),
                "mission_type": MissionType.FLOOD_MONITORING,
                "region": MaricaRegion.ITAIPUACU,
                "route_strategy": RouteStrategyType.FASTEST,
                "priority": MissionPriority.MEDIUM,
            })
        assert result["status"] == MissionStatus.ACTIVE

    def test_drone_status_becomes_active(self, facade, idle_drone):
        with patch("threading.Thread.start"):
            facade.create_and_start_mission({
                "drone_id": str(idle_drone.id),
                "mission_type": MissionType.FLOOD_MONITORING,
                "region": MaricaRegion.ITAIPUACU,
            })
        idle_drone.refresh_from_db()
        assert idle_drone.status == DroneStatus.ACTIVE

    def test_returns_error_for_unknown_drone(self, facade, db):
        result = facade.create_and_start_mission({
            "drone_id": str(uuid.uuid4()),
            "mission_type": MissionType.FLOOD_MONITORING,
            "region": MaricaRegion.ITAIPUACU,
        })
        assert "error" in result

    def test_returns_error_for_active_drone(self, facade, active_drone):
        with patch("threading.Thread.start"):
            result = facade.create_and_start_mission({
                "drone_id": str(active_drone.id),
                "mission_type": MissionType.FLOOD_MONITORING,
                "region": MaricaRegion.ITAIPUACU,
            })
        assert "error" in result

    def test_mission_registered_in_singleton(self, facade, idle_drone):
        with patch("threading.Thread.start"):
            result = facade.create_and_start_mission({
                "drone_id": str(idle_drone.id),
                "mission_type": MissionType.FLOOD_MONITORING,
                "region": MaricaRegion.ITAIPUACU,
            })
        mission_id = str(result["id"])
        cc = MissionControlCenter.get_instance()
        assert cc.get_mission(mission_id) is not None

    def test_background_thread_is_started(self, facade, idle_drone):
        with patch("threading.Thread.start") as mock_start:
            facade.create_and_start_mission({
                "drone_id": str(idle_drone.id),
                "mission_type": MissionType.FLOOD_MONITORING,
                "region": MaricaRegion.ITAIPUACU,
            })
        mock_start.assert_called_once()

    def test_safe_strategy_is_used_when_specified(self, facade, idle_drone):
        with patch("threading.Thread.start"):
            result = facade.create_and_start_mission({
                "drone_id": str(idle_drone.id),
                "mission_type": MissionType.COASTAL_PATROL,
                "region": MaricaRegion.PONTA_NEGRA,
                "route_strategy": RouteStrategyType.SAFE,
            })
        assert result["route_strategy"] == RouteStrategyType.SAFE

    def test_result_contains_route_metrics(self, facade, idle_drone):
        with patch("threading.Thread.start"):
            result = facade.create_and_start_mission({
                "drone_id": str(idle_drone.id),
                "mission_type": MissionType.FLOOD_MONITORING,
                "region": MaricaRegion.ITAIPUACU,
            })
        assert result["distance_km"] is not None
        assert result["estimated_duration_min"] is not None
        assert result["battery_consumption_pct"] is not None
