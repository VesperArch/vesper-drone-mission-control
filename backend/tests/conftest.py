import uuid
import pytest
from rest_framework.test import APIClient

from core.enums import DroneStatus, DroneType, MissionStatus, MissionType, MaricaRegion, RouteStrategyType, MissionPriority


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def idle_drone(db):
    from drones.models import Drone
    return Drone.objects.create(
        name="Sentinel Alpha",
        model="Vesper-S400",
        drone_type=DroneType.SURVEILLANCE,
        status=DroneStatus.IDLE,
        battery_level=100.0,
        speed_kmh=95.0,
        altitude_limit_m=400.0,
        payload_kg=0.5,
        range_km=60.0,
    )


@pytest.fixture
def active_drone(db):
    from drones.models import Drone
    return Drone.objects.create(
        name="Raptor-1",
        model="Vesper-E200",
        drone_type=DroneType.EMERGENCY,
        status=DroneStatus.ACTIVE,
        battery_level=80.0,
        speed_kmh=140.0,
        altitude_limit_m=200.0,
        payload_kg=2.0,
        range_km=35.0,
    )


@pytest.fixture
def delivery_drone(db):
    from drones.models import Drone
    return Drone.objects.create(
        name="Carrier Prime",
        model="Vesper-D800",
        drone_type=DroneType.DELIVERY,
        status=DroneStatus.IDLE,
        battery_level=100.0,
        speed_kmh=65.0,
        altitude_limit_m=150.0,
        payload_kg=8.0,
        range_km=25.0,
    )


@pytest.fixture
def sample_mission(db, idle_drone):
    from missions.models import Mission
    return Mission.objects.create(
        name="Test Mission",
        mission_type=MissionType.FLOOD_MONITORING,
        region=MaricaRegion.ITAIPUACU,
        priority=MissionPriority.MEDIUM,
        assigned_drone=idle_drone,
        route_strategy=RouteStrategyType.FASTEST,
        status=MissionStatus.ACTIVE,
    )


@pytest.fixture
def mission_payload(idle_drone):
    return {
        "drone_id": str(idle_drone.id),
        "mission_type": MissionType.FLOOD_MONITORING,
        "region": MaricaRegion.ITAIPUACU,
        "route_strategy": RouteStrategyType.FASTEST,
        "priority": MissionPriority.MEDIUM,
        "name": "Test Flood Watch",
    }
