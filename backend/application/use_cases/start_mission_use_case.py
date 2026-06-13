from datetime import datetime

from core.enums import DroneStatus, EventType, RouteStrategyType
from core.events import MissionSubject, MissionEventData
from core.singleton import MissionControlCenter
from core.singleton.mission_control_center import MissionRecord
from domain.entities.mission import MissionEntity
from domain.repositories.drone_repository import DroneRepository
from domain.repositories.mission_repository import MissionRepository, MissionCreateData
from missions.observers import LoggerObserver, AlertObserver, MissionStatusObserver
from missions.strategies import FastestRouteStrategy, SafeRouteStrategy, BatterySavingStrategy


_STRATEGY_MAP = {
    RouteStrategyType.FASTEST: FastestRouteStrategy(),
    RouteStrategyType.SAFE: SafeRouteStrategy(),
    RouteStrategyType.BATTERY_SAVING: BatterySavingStrategy(),
}


class DroneNotFoundError(Exception):
    def __init__(self, drone_id: str):
        super().__init__(f"Drone {drone_id} not found.")


class DroneUnavailableError(Exception):
    def __init__(self, name: str, status: str):
        super().__init__(f"Drone {name} is currently {status} and unavailable.")


def _build_subject() -> MissionSubject:
    subject = MissionSubject()
    subject.attach(LoggerObserver())
    subject.attach(AlertObserver())
    subject.attach(MissionStatusObserver())
    return subject


class StartMissionUseCase:
    """
    Application Use Case: validates, computes route, persists and fires events.
    Depends only on domain abstractions — zero Django/ORM imports here.
    """

    def __init__(self, drone_repo: DroneRepository, mission_repo: MissionRepository) -> None:
        self._drone_repo = drone_repo
        self._mission_repo = mission_repo
        self._control = MissionControlCenter.get_instance()

    def execute(self, payload: dict) -> MissionEntity:
        drone_id = str(payload["drone_id"])
        mission_type: str = payload["mission_type"]
        region: str = payload["region"]
        strategy_name: str = payload.get("route_strategy", RouteStrategyType.FASTEST)
        priority: str = payload.get("priority", "MEDIUM")
        name: str = payload.get("name", f"{mission_type} @ {region}")

        # Step 1: validate drone via repository abstraction
        drone = self._drone_repo.get_by_id(drone_id)
        if drone is None:
            raise DroneNotFoundError(drone_id)
        if drone.status not in (DroneStatus.IDLE, DroneStatus.CHARGING):
            raise DroneUnavailableError(drone.name, drone.status)

        # Step 2: calculate route (pure domain logic via Strategy)
        strategy = _STRATEGY_MAP.get(strategy_name, FastestRouteStrategy())
        route = strategy.calculate_route(
            origin="Centro",
            destination=region,
            drone_speed_kmh=drone.speed_kmh,
            drone_range_km=drone.range_km,
        )

        # Step 3: persist mission via repository abstraction
        mission = self._mission_repo.create(MissionCreateData(
            name=name,
            mission_type=mission_type,
            region=region,
            priority=priority,
            route_strategy=strategy_name,
            drone_id=drone_id,
            estimated_duration_min=route.estimated_duration_min,
            distance_km=route.distance_km,
            battery_consumption_pct=route.battery_consumption_pct,
            weather_risk_score=route.weather_risk_score,
            waypoints=route.waypoints,
            route_notes=route.notes,
        ))

        # Step 4: update drone status
        drone.status = DroneStatus.ACTIVE
        self._drone_repo.save(drone)

        # Step 5: register in Singleton
        self._control.register_mission(MissionRecord(
            mission_id=mission.id,
            mission_type=mission_type,
            region=region,
            drone_id=drone_id,
            strategy=strategy_name,
            status="ACTIVE",
        ))

        # Step 6: fire MISSION_STARTED event via Observer chain
        started_msg = f"Mission '{name}' deployed to {region} via {strategy_name} route."
        _build_subject().notify(MissionEventData(
            mission_id=mission.id,
            event_type=EventType.MISSION_STARTED,
            message=started_msg,
            drone_id=drone_id,
            severity="INFO",
            timestamp=datetime.now(),
        ))
        self._mission_repo.log_event(mission.id, EventType.MISSION_STARTED, started_msg, "INFO")

        return mission
