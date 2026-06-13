"""
Unit tests for StartMissionUseCase.
Repositories are replaced with in-memory fakes — no Django, no DB.
"""
import uuid
from typing import Optional
from unittest.mock import patch

import pytest

from application.use_cases.start_mission_use_case import (
    StartMissionUseCase,
    DroneNotFoundError,
    DroneUnavailableError,
)
from core.singleton import MissionControlCenter
from domain.entities.drone import DroneEntity
from domain.entities.mission import MissionEntity
from domain.repositories.drone_repository import DroneRepository
from domain.repositories.mission_repository import MissionRepository, MissionCreateData


# ---------------------------------------------------------------------------
# In-memory fakes (no side-effects, no DB)
# ---------------------------------------------------------------------------

class FakeDroneRepository(DroneRepository):
    def __init__(self, drone: Optional[DroneEntity] = None):
        self._drone = drone
        self.saved: list[DroneEntity] = []

    def get_by_id(self, drone_id: str) -> Optional[DroneEntity]:
        if self._drone and str(self._drone.id) == drone_id:
            return self._drone
        return None

    def save(self, drone: DroneEntity) -> None:
        self.saved.append(drone)

    def list_all(self) -> list[DroneEntity]:
        return [self._drone] if self._drone else []


class FakeMissionRepository(MissionRepository):
    def __init__(self):
        self.events: list[dict] = []
        self.statuses: list[tuple] = []

    def create(self, data: MissionCreateData) -> MissionEntity:
        return MissionEntity(
            id=str(uuid.uuid4()),
            name=data.name,
            mission_type=data.mission_type,
            region=data.region,
            priority=data.priority,
            route_strategy=data.route_strategy,
            status="ACTIVE",
            assigned_drone_id=data.drone_id,
            estimated_duration_min=data.estimated_duration_min,
            distance_km=data.distance_km,
            battery_consumption_pct=data.battery_consumption_pct,
            weather_risk_score=data.weather_risk_score,
            waypoints=data.waypoints,
            route_notes=data.route_notes,
        )

    def get_by_id(self, mission_id: str) -> Optional[MissionEntity]:
        return None

    def list_all(self) -> list[MissionEntity]:
        return []

    def log_event(self, mission_id: str, event_type: str, message: str, severity: str) -> None:
        self.events.append({"mission_id": mission_id, "event_type": event_type, "severity": severity})

    def update_status(self, mission_id: str, status: str, completed_at=None) -> None:
        self.statuses.append((mission_id, status))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_singleton():
    MissionControlCenter._instance = None
    MissionControlCenter._initialized = False
    yield
    MissionControlCenter._instance = None
    MissionControlCenter._initialized = False


def _idle_drone(status="IDLE") -> DroneEntity:
    return DroneEntity(
        id=str(uuid.uuid4()),
        name="Alpha-1",
        drone_type="SURVEILLANCE",
        status=status,
        speed_kmh=80.0,
        range_km=40.0,
        battery_level=100.0,
    )


def _payload(drone_id: str, strategy: str = "FASTEST") -> dict:
    return {
        "drone_id": drone_id,
        "mission_type": "SURVEILLANCE",
        "region": "Itaipuaçu",
        "priority": "HIGH",
        "route_strategy": strategy,
        "name": "Op Alpha",
    }


# ---------------------------------------------------------------------------
# Tests: happy path
# ---------------------------------------------------------------------------

class TestStartMissionSuccess:
    def test_returns_mission_entity(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert isinstance(result, MissionEntity)

    def test_mission_status_is_active(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert result.status == "ACTIVE"

    def test_mission_name_comes_from_payload(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert result.name == "Op Alpha"

    def test_mission_uses_correct_region(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert result.region == "Itaipuaçu"

    def test_drone_status_updated_to_active(self):
        drone = _idle_drone()
        drone_repo = FakeDroneRepository(drone)
        use_case = StartMissionUseCase(drone_repo, FakeMissionRepository())
        use_case.execute(_payload(drone.id))
        assert len(drone_repo.saved) == 1
        assert drone_repo.saved[0].status == "ACTIVE"

    def test_mission_started_event_logged(self):
        drone = _idle_drone()
        mission_repo = FakeMissionRepository()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), mission_repo)
        use_case.execute(_payload(drone.id))
        assert any(e["event_type"] == "MISSION_STARTED" for e in mission_repo.events)

    def test_mission_registered_in_singleton(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        control = MissionControlCenter.get_instance()
        assert control.get_mission(result.id) is not None

    def test_route_metrics_are_populated(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert result.distance_km is not None and result.distance_km > 0
        assert result.estimated_duration_min is not None and result.estimated_duration_min > 0
        assert result.battery_consumption_pct is not None

    def test_charging_drone_is_also_available(self):
        drone = _idle_drone(status="CHARGING")
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert result.status == "ACTIVE"

    def test_safe_strategy_sets_strategy_field(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id, strategy="SAFE"))
        assert result.route_strategy == "SAFE"

    def test_battery_saving_strategy_sets_strategy_field(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id, strategy="BATTERY_SAVING"))
        assert result.route_strategy == "BATTERY_SAVING"

    def test_mission_id_is_string(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert isinstance(result.id, str) and len(result.id) > 0

    def test_assigned_drone_id_matches(self):
        drone = _idle_drone()
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        result = use_case.execute(_payload(drone.id))
        assert result.assigned_drone_id == str(drone.id)


# ---------------------------------------------------------------------------
# Tests: error cases
# ---------------------------------------------------------------------------

class TestStartMissionErrors:
    def test_raises_drone_not_found_for_unknown_id(self):
        use_case = StartMissionUseCase(FakeDroneRepository(None), FakeMissionRepository())
        with pytest.raises(DroneNotFoundError):
            use_case.execute(_payload("nonexistent-id"))

    def test_error_message_includes_drone_id(self):
        use_case = StartMissionUseCase(FakeDroneRepository(None), FakeMissionRepository())
        fake_id = "dead-beef-1234"
        with pytest.raises(DroneNotFoundError, match=fake_id):
            use_case.execute(_payload(fake_id))

    def test_raises_drone_unavailable_for_active_drone(self):
        drone = _idle_drone(status="ACTIVE")
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        with pytest.raises(DroneUnavailableError):
            use_case.execute(_payload(drone.id))

    def test_raises_drone_unavailable_for_maintenance_drone(self):
        drone = _idle_drone(status="MAINTENANCE")
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        with pytest.raises(DroneUnavailableError):
            use_case.execute(_payload(drone.id))

    def test_unavailable_error_message_contains_drone_name(self):
        drone = _idle_drone(status="ACTIVE")
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        with pytest.raises(DroneUnavailableError, match="Alpha-1"):
            use_case.execute(_payload(drone.id))

    def test_unavailable_error_message_contains_status(self):
        drone = _idle_drone(status="ACTIVE")
        use_case = StartMissionUseCase(FakeDroneRepository(drone), FakeMissionRepository())
        with pytest.raises(DroneUnavailableError, match="ACTIVE"):
            use_case.execute(_payload(drone.id))

    def test_drone_not_saved_when_not_found(self):
        drone_repo = FakeDroneRepository(None)
        use_case = StartMissionUseCase(drone_repo, FakeMissionRepository())
        try:
            use_case.execute(_payload("ghost-id"))
        except DroneNotFoundError:
            pass
        assert drone_repo.saved == []

    def test_no_event_logged_when_drone_not_found(self):
        mission_repo = FakeMissionRepository()
        use_case = StartMissionUseCase(FakeDroneRepository(None), mission_repo)
        try:
            use_case.execute(_payload("ghost-id"))
        except DroneNotFoundError:
            pass
        assert mission_repo.events == []
