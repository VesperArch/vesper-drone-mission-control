import pytest
from unittest.mock import patch
from pytest_bdd import scenarios, given, when, then, parsers
from rest_framework.test import APIClient

from core.enums import DroneStatus, DroneType, MissionStatus, MissionType, MaricaRegion, RouteStrategyType, MissionPriority

scenarios("../../features/mission_lifecycle.feature")


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def response_holder():
    return {}


@given(parsers.parse('a drone with status "{drone_status}" exists in the database'), target_fixture="target_drone")
def create_drone_with_status(db, drone_status):
    from drones.models import Drone
    return Drone.objects.create(
        name="BDD Test Drone",
        model="Vesper-Test",
        drone_type=DroneType.SURVEILLANCE,
        status=drone_status,
        battery_level=100.0,
        speed_kmh=95.0,
        altitude_limit_m=400.0,
        payload_kg=0.5,
        range_km=60.0,
    )


@when("I submit a mission creation request for that drone", target_fixture="api_response")
def submit_mission(client, target_drone):
    payload = {
        "drone_id": str(target_drone.id),
        "mission_type": MissionType.FLOOD_MONITORING,
        "region": MaricaRegion.ITAIPUACU,
        "route_strategy": RouteStrategyType.FASTEST,
        "priority": MissionPriority.MEDIUM,
        "name": "BDD Test Mission",
    }
    with patch("threading.Thread.start"):
        return client.post("/api/missions/create/", payload, format="json")


@then(parsers.parse('the mission status should be "{expected_status}"'))
def check_mission_status(api_response, expected_status):
    assert api_response.status_code == 201
    assert api_response.data["status"] == expected_status


@then("the drone status should change to \"ACTIVE\"")
def check_drone_active(target_drone):
    target_drone.refresh_from_db()
    assert target_drone.status == DroneStatus.ACTIVE


@then("the response should contain an error message")
def check_error_response(api_response):
    assert api_response.status_code in (409, 400)
    assert "error" in api_response.data
