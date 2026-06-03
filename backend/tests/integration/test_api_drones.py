import pytest
import uuid
from rest_framework.test import APIClient

from drones.models import Drone
from core.enums import DroneStatus, DroneType


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestListDrones:
    def test_returns_200(self, client, idle_drone):
        response = client.get("/api/drones/")
        assert response.status_code == 200

    def test_returns_list(self, client, idle_drone):
        response = client.get("/api/drones/")
        assert isinstance(response.data, list)

    def test_includes_created_drone(self, client, idle_drone):
        response = client.get("/api/drones/")
        ids = [str(d["id"]) for d in response.data]
        assert str(idle_drone.id) in ids

    def test_empty_database_returns_empty_list(self, client, db):
        response = client.get("/api/drones/")
        assert response.status_code == 200
        assert response.data == []

    def test_drone_fields_present(self, client, idle_drone):
        response = client.get("/api/drones/")
        drone = response.data[0]
        for field in ["id", "name", "model", "drone_type", "status", "battery_level"]:
            assert field in drone


@pytest.mark.django_db
class TestGetDrone:
    def test_returns_200_for_existing_drone(self, client, idle_drone):
        response = client.get(f"/api/drones/{idle_drone.id}/")
        assert response.status_code == 200

    def test_returns_correct_drone(self, client, idle_drone):
        response = client.get(f"/api/drones/{idle_drone.id}/")
        assert str(response.data["id"]) == str(idle_drone.id)
        assert response.data["name"] == idle_drone.name

    def test_returns_404_for_unknown_id(self, client, db):
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/drones/{fake_id}/")
        assert response.status_code == 404

    def test_returns_correct_status(self, client, idle_drone):
        response = client.get(f"/api/drones/{idle_drone.id}/")
        assert response.data["status"] == DroneStatus.IDLE
