"""
DESIGN PATTERN: Facade
───────────────────────
DroneMissionFacade unifies the entire mission lifecycle behind a single, clean
API surface. Callers (Django views, management commands, tests) interact with
ONE method rather than orchestrating five subsystems manually.

Without the Facade, every caller would need to:
  1. Resolve the correct route strategy
  2. Retrieve the drone from the factory
  3. Instantiate all three observers
  4. Attach observers to the subject
  5. Call the mission service to persist the record
  6. Trigger the simulation
  7. Update the Singleton registry

With the Facade, that complexity is hidden behind:
  facade.create_and_start_mission(data)

Why Facade here?
  The pattern is appropriate when a subsystem is intrinsically complex but the
  calling code only needs a narrow workflow. It reduces coupling between layers
  and makes the system far easier to test in isolation (mock the facade, not all
  5 subsystems). It is NOT a God-object — it delegates, never implements.
"""

from __future__ import annotations

import random
import threading
import time as _time
from datetime import datetime
from typing import Any

from loguru import logger

from core.enums import (
    EventType,
    MissionStatus,
    RouteStrategyType,
    DroneStatus,
)
from core.events import MissionEventData, MissionSubject
from core.singleton import MissionControlCenter
from core.singleton.mission_control_center import MissionRecord, DroneRecord
from missions.strategies import (
    RouteStrategy,
    FastestRouteStrategy,
    SafeRouteStrategy,
    BatterySavingStrategy,
    RouteResult,
)
from missions.observers import LoggerObserver, AlertObserver, MissionStatusObserver


# ── Demo time compression ─────────────────────────────────────────────────────
# 1 simulated minute → 6 real seconds  (20-min flight = ~2 min demo)
DEMO_SPEED_FACTOR = 10


# ── Strategy registry ────────────────────────────────────────────────────────

_STRATEGY_MAP: dict[str, RouteStrategy] = {
    RouteStrategyType.FASTEST: FastestRouteStrategy(),
    RouteStrategyType.SAFE: SafeRouteStrategy(),
    RouteStrategyType.BATTERY_SAVING: BatterySavingStrategy(),
}


def _get_strategy(name: str) -> RouteStrategy:
    return _STRATEGY_MAP.get(name, FastestRouteStrategy())


# ── Mid-mission event templates ───────────────────────────────────────────────

_WEATHER_EVENTS = [
    ("BAD_WEATHER",        "Rainstorm detected over {region} — wind gusts 60 km/h.", "ALERT"),
    ("LOW_BATTERY",        "Battery below 25% threshold — efficiency mode engaged.", "WARNING"),
    ("SIGNAL_LOST",        "Telemetry signal unstable — reconnecting to ground station.", "WARNING"),
    ("OBSTACLE_DETECTED",  "Obstacle detected in flight corridor — auto-rerouting.", "WARNING"),
]


def _build_subject() -> MissionSubject:
    subject = MissionSubject()
    subject.attach(LoggerObserver())
    subject.attach(AlertObserver())
    subject.attach(MissionStatusObserver())
    return subject


# ── Facade ────────────────────────────────────────────────────────────────────

class DroneMissionFacade:
    """
    Facade: single entry point for the full mission lifecycle.

    Subsystems coordinated:
      • MissionControlCenter (Singleton)   — global state registry
      • DroneFactory (Factory Method)      — drone specification lookup
      • RouteStrategy (Strategy)           — route computation
      • MissionSubject + Observers         — event broadcasting
      • Django ORM models                  — persistence
    """

    def __init__(self) -> None:
        self._control = MissionControlCenter.get_instance()

    # ── Public API ────────────────────────────────────────────────────────────

    def create_and_start_mission(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Start a mission and return immediately with status ACTIVE.
        The full lifecycle (mid-mission events → completion) runs in a
        background daemon thread after DEMO_SPEED_FACTOR compression.

        Steps in this call:
          1. Validate and load the drone record
          2. Select and execute the route strategy
          3. Persist the Mission model (status=ACTIVE)
          4. Fire MISSION_STARTED through Observer chain
          5. Return the serialized ACTIVE mission

        The background thread handles:
          6. Probabilistic mid-mission events at realistic intervals
          7. MISSION_COMPLETED event
          8. DB + Singleton sync
        """
        from drones.models import Drone
        from missions.models import Mission, MissionEvent

        drone_id: str    = str(payload["drone_id"])
        mission_type: str = payload["mission_type"]
        region: str      = payload["region"]
        strategy_name: str = payload.get("route_strategy", RouteStrategyType.FASTEST)
        priority: str    = payload.get("priority", "MEDIUM")
        name: str        = payload.get("name", f"{mission_type} @ {region}")

        logger.info(f"[Facade] ▶ Launching mission — type={mission_type} region={region} strategy={strategy_name}")

        # ── Step 1: Load drone ────────────────────────────────────────────────
        try:
            drone_obj = Drone.objects.get(id=drone_id)
        except Drone.DoesNotExist:
            return {"error": f"Drone {drone_id} not found."}

        if drone_obj.status not in (DroneStatus.IDLE, DroneStatus.CHARGING):
            return {"error": f"Drone {drone_obj.name} is currently {drone_obj.status} and unavailable."}

        # ── Step 2: Compute route via Strategy ────────────────────────────────
        strategy: RouteStrategy = _get_strategy(strategy_name)
        route = strategy.calculate_route(
            origin="Centro",
            destination=region,
            drone_speed_kmh=drone_obj.speed_kmh,
            drone_range_km=drone_obj.range_km,
        )
        logger.debug(f"[Facade] Route: {route.distance_km} km / {route.estimated_duration_min} min")

        # ── Step 3: Persist Mission as ACTIVE ─────────────────────────────────
        mission = Mission.objects.create(
            name=name,
            mission_type=mission_type,
            region=region,
            priority=priority,
            assigned_drone=drone_obj,
            route_strategy=strategy_name,
            status=MissionStatus.ACTIVE,
            estimated_duration_min=route.estimated_duration_min,
            distance_km=route.distance_km,
            battery_consumption_pct=route.battery_consumption_pct,
            weather_risk_score=route.weather_risk_score,
            waypoints=route.waypoints,
            route_notes=route.notes,
            started_at=datetime.now(),
        )

        # Mark drone as busy
        drone_obj.status = DroneStatus.ACTIVE
        drone_obj.save()

        mission_id = str(mission.id)

        self._control.register_mission(MissionRecord(
            mission_id=mission_id,
            mission_type=mission_type,
            region=region,
            drone_id=drone_id,
            strategy=strategy_name,
            status=MissionStatus.ACTIVE,
        ))

        # ── Step 4: Fire MISSION_STARTED ──────────────────────────────────────
        subject = _build_subject()
        started_msg = f"Mission '{name}' deployed to {region} via {strategy_name} route."
        subject.notify(MissionEventData(
            mission_id=mission_id,
            event_type=EventType.MISSION_STARTED,
            message=started_msg,
            drone_id=drone_id,
            severity="INFO",
        ))
        MissionEvent.objects.create(
            mission=mission,
            event_type=EventType.MISSION_STARTED,
            message=started_msg,
            severity="INFO",
        )

        # ── Step 5: Spawn background lifecycle thread ─────────────────────────
        demo_sec = max(30.0, route.estimated_duration_min * 60.0 / DEMO_SPEED_FACTOR)
        logger.info(f"[Facade] Mission {mission_id[:8]}… is ACTIVE — completes in {demo_sec:.0f}s (demo)")

        t = threading.Thread(
            target=self._run_lifecycle,
            args=(mission_id, drone_id, region, name, drone_obj.battery_level,
                  route.battery_consumption_pct, demo_sec),
            daemon=True,
            name=f"mission-{mission_id[:8]}",
        )
        t.start()

        # ── Step 6: Return ACTIVE mission ─────────────────────────────────────
        from missions.serializers import MissionSerializer
        return MissionSerializer(mission).data

    # ── Background lifecycle ──────────────────────────────────────────────────

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
        """
        Runs in a daemon thread. Sleeps through the compressed demo duration,
        fires mid-mission events at realistic intervals, then marks the mission
        COMPLETED and syncs DB + Singleton.
        """
        from django.db import close_old_connections
        close_old_connections()

        from missions.models import MissionEvent, Mission
        from drones.models import Drone

        try:
            # Choose 0-2 random mid-mission event times (as fractions of duration)
            num_events = random.randint(0, 2)
            event_fracs = sorted(random.uniform(0.15, 0.80) for _ in range(num_events))

            elapsed = 0.0
            for frac in event_fracs:
                wait = frac * demo_sec - elapsed
                _time.sleep(max(0, wait))
                elapsed = frac * demo_sec

                ev_type, msg_tpl, severity = random.choice(_WEATHER_EVENTS)
                message = msg_tpl.format(region=region)

                subject = _build_subject()
                subject.notify(MissionEventData(
                    mission_id=mission_id,
                    event_type=ev_type,
                    message=message,
                    drone_id=drone_id,
                    severity=severity,
                ))
                MissionEvent.objects.create(
                    mission_id=mission_id,
                    event_type=ev_type,
                    message=message,
                    severity=severity,
                )
                logger.debug(f"[Lifecycle] {ev_type} fired for mission {mission_id[:8]}…")

            # Wait for the remainder of the demo duration
            _time.sleep(max(0, demo_sec - elapsed))

            # Fire MISSION_COMPLETED
            completed_msg = f"Mission '{name}' completed successfully. Drone returning to base."
            subject = _build_subject()
            subject.notify(MissionEventData(
                mission_id=mission_id,
                event_type=EventType.MISSION_COMPLETED,
                message=completed_msg,
                drone_id=drone_id,
                severity="SUCCESS",
            ))
            MissionEvent.objects.create(
                mission_id=mission_id,
                event_type=EventType.MISSION_COMPLETED,
                message=completed_msg,
                severity="SUCCESS",
            )

            # Sync DB
            Mission.objects.filter(id=mission_id).update(
                status=MissionStatus.COMPLETED,
                completed_at=datetime.now(),
            )
            Drone.objects.filter(id=drone_id).update(
                status=DroneStatus.IDLE,
                battery_level=max(10.0, drone_battery - battery_draw),
            )

            logger.success(f"[Facade] ✔ Mission {mission_id[:8]}… COMPLETED after {demo_sec:.0f}s")

        except Exception as exc:
            logger.error(f"[Facade] ✗ Lifecycle thread error for {mission_id[:8]}: {exc}")
            try:
                Mission.objects.filter(id=mission_id).update(status=MissionStatus.FAILED)
                Drone.objects.filter(id=drone_id).update(status=DroneStatus.IDLE)
            except Exception:
                pass
        finally:
            close_old_connections()
