import pytest
import uuid
from unittest.mock import patch
from rest_framework.test import APIClient

from missions.models import Mission, MissionEvent
from core.enums import MissionStatus, DroneStatus, MissionType, MaricaRegion, RouteStrategyType, MissionPriority


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def mission_create_payload(idle_drone):
    return {
        "drone_id": str(idle_drone.id),
        "mission_type": MissionType.FLOOD_MONITORING,
        "region": MaricaRegion.ITAIPUACU,
        "route_strategy": RouteStrategyType.FASTEST,
        "priority": MissionPriority.MEDIUM,
        "name": "Test Flood Watch",
    }


@pytest.mark.django_db
class TestListMissions:
    def test_returns_200(self, client, db):
        response = client.get("/api/missions/")
        assert response.status_code == 200

    def test_returns_list(self, client, db):
        response = client.get("/api/missions/")
        assert isinstance(response.data, list)

    def test_includes_existing_mission(self, client, sample_mission):
        response = client.get("/api/missions/")
        ids = [str(m["id"]) for m in response.data]
        assert str(sample_mission.id) in ids

    def test_mission_fields_present(self, client, sample_mission):
        response = client.get("/api/missions/")
        mission = response.data[0]
        for field in ["id", "name", "mission_type", "region", "status"]:
            assert field in mission


@pytest.mark.django_db
class TestGetMission:
    def test_returns_200_for_existing_mission(self, client, sample_mission):
        response = client.get(f"/api/missions/{sample_mission.id}/")
        assert response.status_code == 200

    def test_returns_correct_mission(self, client, sample_mission):
        response = client.get(f"/api/missions/{sample_mission.id}/")
        assert str(response.data["id"]) == str(sample_mission.id)

    def test_returns_404_for_unknown_id(self, client, db):
        response = client.get(f"/api/missions/{uuid.uuid4()}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestCreateMission:
    def test_creates_mission_with_idle_drone(self, client, mission_create_payload):
        with patch("threading.Thread.start"):
            response = client.post("/api/missions/create/", mission_create_payload, format="json")
        assert response.status_code == 201

    def test_mission_status_is_active(self, client, mission_create_payload):
        with patch("threading.Thread.start"):
            response = client.post("/api/missions/create/", mission_create_payload, format="json")
        assert response.data["status"] == MissionStatus.ACTIVE

    def test_drone_becomes_active_after_mission_start(self, client, mission_create_payload, idle_drone):
        with patch("threading.Thread.start"):
            client.post("/api/missions/create/", mission_create_payload, format="json")
        idle_drone.refresh_from_db()
        assert idle_drone.status == DroneStatus.ACTIVE

    def test_returns_409_with_active_drone(self, client, active_drone):
        payload = {
            "drone_id": str(active_drone.id),
            "mission_type": MissionType.FLOOD_MONITORING,
            "region": MaricaRegion.ITAIPUACU,
            "route_strategy": RouteStrategyType.FASTEST,
            "priority": MissionPriority.MEDIUM,
            "name": "Conflict Mission",
        }
        with patch("threading.Thread.start"):
            response = client.post("/api/missions/create/", payload, format="json")
        assert response.status_code == 409
        assert "error" in response.data

    def test_returns_409_with_unknown_drone_id(self, client, db):
        payload = {
            "drone_id": str(uuid.uuid4()),
            "mission_type": MissionType.FLOOD_MONITORING,
            "region": MaricaRegion.ITAIPUACU,
            "route_strategy": RouteStrategyType.FASTEST,
            "priority": MissionPriority.MEDIUM,
            "name": "Ghost Mission",
        }
        with patch("threading.Thread.start"):
            response = client.post("/api/missions/create/", payload, format="json")
        assert response.status_code == 409

    def test_returns_400_with_missing_required_field(self, client, db):
        response = client.post("/api/missions/create/", {"drone_id": str(uuid.uuid4())}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestMissionLogs:
    def test_returns_200(self, client, db):
        response = client.get("/api/missions/logs/")
        assert response.status_code == 200

    def test_returns_list(self, client, db):
        response = client.get("/api/missions/logs/")
        assert isinstance(response.data, list)

    def test_includes_mission_events(self, client, sample_mission):
        MissionEvent.objects.create(
            mission=sample_mission,
            event_type="MISSION_STARTED",
            message="Mission started",
            severity="INFO",
        )
        response = client.get("/api/missions/logs/")
        assert len(response.data) >= 1
