"""
DESIGN PATTERN: Facade
───────────────────────
DroneMissionFacade unifies the mission lifecycle behind a single entry point.
After the Clean Architecture refactor, it no longer contains business logic —
that lives in StartMissionUseCase. The Facade now:
  1. Wires concrete repositories (infrastructure layer)
  2. Delegates synchronous logic to StartMissionUseCase (application layer)
  3. Manages the background lifecycle thread (coordination, not business logic)

Dependency direction respected:
  Facade → UseCase → Repository Interface ← Repository Implementation
"""

from __future__ import annotations

import random
import threading
import time as _time
from datetime import datetime
from typing import Any

from loguru import logger

from application.use_cases.start_mission_use_case import (
    StartMissionUseCase,
    DroneNotFoundError,
    DroneUnavailableError,
    _build_subject,
)
from core.enums import EventType, MissionStatus, DroneStatus
from core.events import MissionEventData
from domain.repositories.drone_repository import DroneRepository
from domain.repositories.mission_repository import MissionRepository
from infrastructure.repositories.django_drone_repository import DjangoDroneRepository
from infrastructure.repositories.django_mission_repository import DjangoMissionRepository

DEMO_SPEED_FACTOR = 10

_WEATHER_EVENTS = [
    ("BAD_WEATHER",       "Rainstorm detected over {region} — wind gusts 60 km/h.", "ALERT"),
    ("LOW_BATTERY",       "Battery below 25% threshold — efficiency mode engaged.", "WARNING"),
    ("SIGNAL_LOST",       "Telemetry signal unstable — reconnecting to ground station.", "WARNING"),
    ("OBSTACLE_DETECTED", "Obstacle detected in flight corridor — auto-rerouting.", "WARNING"),
]


class DroneMissionFacade:
    """
    Facade: wires repositories and delegates to StartMissionUseCase.
    Accepts injectable repositories for testability.
    """

    def __init__(
        self,
        drone_repo: DroneRepository | None = None,
        mission_repo: MissionRepository | None = None,
    ) -> None:
        self._drone_repo = drone_repo or DjangoDroneRepository()
        self._mission_repo = mission_repo or DjangoMissionRepository()

    def create_and_start_mission(self, payload: dict[str, Any]) -> dict[str, Any]:
        use_case = StartMissionUseCase(self._drone_repo, self._mission_repo)

        try:
            mission = use_case.execute(payload)
        except (DroneNotFoundError, DroneUnavailableError) as exc:
            return {"error": str(exc)}

        drone = self._drone_repo.get_by_id(str(payload["drone_id"]))
        demo_sec = max(30.0, (mission.estimated_duration_min or 20.0) * 60.0 / DEMO_SPEED_FACTOR)

        logger.info(f"[Facade] Mission {mission.id[:8]}… is ACTIVE — completes in {demo_sec:.0f}s (demo)")

        t = threading.Thread(
            target=self._run_lifecycle,
            args=(
                mission.id,
                str(payload["drone_id"]),
                payload["region"],
                mission.name,
                drone.battery_level if drone else 100.0,
                mission.battery_consumption_pct or 0.0,
                demo_sec,
            ),
            daemon=True,
            name=f"mission-{mission.id[:8]}",
        )
        t.start()

        return self._serialize(mission)

    def _run_lifecycle(
        self,
        mission_id: str,
        drone_id: str,
        region: str,
        name: str,
        drone_battery: float,
        battery_draw: float,
        demo_sec: float,
    ) -> None:
        from django.db import close_old_connections
        close_old_connections()

        try:
            num_events = random.randint(0, 2)
            event_fracs = sorted(random.uniform(0.15, 0.80) for _ in range(num_events))

            elapsed = 0.0
            for frac in event_fracs:
                wait = frac * demo_sec - elapsed
                _time.sleep(max(0, wait))
                elapsed = frac * demo_sec

                ev_type, msg_tpl, severity = random.choice(_WEATHER_EVENTS)
                message = msg_tpl.format(region=region)

                _build_subject().notify(MissionEventData(
                    mission_id=mission_id,
                    event_type=ev_type,
                    message=message,
                    drone_id=drone_id,
                    severity=severity,
                ))
                self._mission_repo.log_event(mission_id, ev_type, message, severity)

            _time.sleep(max(0, demo_sec - elapsed))

            completed_msg = f"Mission '{name}' completed successfully. Drone returning to base."
            _build_subject().notify(MissionEventData(
                mission_id=mission_id,
                event_type=EventType.MISSION_COMPLETED,
                message=completed_msg,
                drone_id=drone_id,
                severity="SUCCESS",
            ))
            self._mission_repo.log_event(mission_id, EventType.MISSION_COMPLETED, completed_msg, "SUCCESS")
            self._mission_repo.update_status(mission_id, MissionStatus.COMPLETED, completed_at=datetime.now())

            drone_entity = self._drone_repo.get_by_id(drone_id)
            if drone_entity:
                drone_entity.status = DroneStatus.IDLE
                drone_entity.battery_level = max(10.0, drone_battery - battery_draw)
                self._drone_repo.save(drone_entity)

            logger.success(f"[Facade] ✔ Mission {mission_id[:8]}… COMPLETED")

        except Exception as exc:
            logger.error(f"[Facade] ✗ Lifecycle error for {mission_id[:8]}: {exc}")
            try:
                self._mission_repo.update_status(mission_id, MissionStatus.FAILED)
                drone_entity = self._drone_repo.get_by_id(drone_id)
                if drone_entity:
                    drone_entity.status = DroneStatus.IDLE
                    self._drone_repo.save(drone_entity)
            except Exception:
                pass
        finally:
            from django.db import close_old_connections
            close_old_connections()

    @staticmethod
    def _serialize(mission) -> dict[str, Any]:
        return {
            "id": mission.id,
            "name": mission.name,
            "mission_type": mission.mission_type,
            "region": mission.region,
            "priority": mission.priority,
            "route_strategy": mission.route_strategy,
            "status": mission.status,
            "assigned_drone_id": mission.assigned_drone_id,
            "estimated_duration_min": mission.estimated_duration_min,
            "distance_km": mission.distance_km,
            "battery_consumption_pct": mission.battery_consumption_pct,
            "weather_risk_score": mission.weather_risk_score,
            "waypoints": mission.waypoints,
            "route_notes": mission.route_notes,
        }
