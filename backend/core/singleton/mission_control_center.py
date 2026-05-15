"""
DESIGN PATTERN: Singleton
─────────────────────────
MissionControlCenter is the central nervous system of Vesper's drone fleet.

Only ONE instance may exist for the entire application lifetime. This guarantees
that all subsystems (API, facade, observers) share the exact same state:
active missions, registered drones, and accumulated event log.

Why Singleton here?
  A city's mission-control room is physically unique. Having two independent
  registries diverging in state would be operationally catastrophic — a drone
  marked IDLE in one registry could be double-dispatched by another. The pattern
  enforces that invariant at the language level.

Implementation:
  _instance class variable + get_instance() class method. The constructor is
  intentionally kept private-by-convention (prefix _) and guarded by a flag so
  external callers cannot bypass get_instance().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from loguru import logger


@dataclass
class DroneRecord:
    drone_id: str
    drone_name: str
    drone_type: str
    status: str
    battery_level: float


@dataclass
class MissionRecord:
    mission_id: str
    mission_type: str
    region: str
    drone_id: str
    strategy: str
    status: str
    started_at: datetime = field(default_factory=datetime.now)


@dataclass
class EventRecord:
    mission_id: str
    event_type: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


class MissionControlCenter:
    """
    Singleton: guarantees a single, globally-shared mission control state.
    """

    _instance: Optional[MissionControlCenter] = None
    _initialized: bool = False

    def __new__(cls) -> MissionControlCenter:
        # ── Singleton guard: only instantiate once ──────────────────────────
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Guard re-initialisation on repeated calls to the constructor.
        if self._initialized:
            return
        self._initialized = True

        self._active_missions: dict[str, MissionRecord] = {}
        self._registered_drones: dict[str, DroneRecord] = {}
        self._event_log: list[EventRecord] = []
        self._total_missions_executed: int = 0
        self._total_events_fired: int = 0

        logger.info("[MissionControlCenter] ✦ Singleton instance created — control centre online.")

    # ── Factory access point ─────────────────────────────────────────────────
    @classmethod
    def get_instance(cls) -> MissionControlCenter:
        """Return the single global instance, creating it on first call."""
        if cls._instance is None:
            cls()
        return cls._instance  # type: ignore[return-value]

    # ── Drone registry ───────────────────────────────────────────────────────
    def register_drone(self, drone: DroneRecord) -> None:
        self._registered_drones[drone.drone_id] = drone
        logger.debug(f"[MissionControlCenter] Drone registered → {drone.drone_name} ({drone.drone_type})")

    def update_drone_status(self, drone_id: str, status: str, battery_level: float | None = None) -> None:
        if drone_id in self._registered_drones:
            self._registered_drones[drone_id].status = status
            if battery_level is not None:
                self._registered_drones[drone_id].battery_level = battery_level

    def get_drone(self, drone_id: str) -> Optional[DroneRecord]:
        return self._registered_drones.get(drone_id)

    def list_drones(self) -> list[DroneRecord]:
        return list(self._registered_drones.values())

    # ── Mission tracking ─────────────────────────────────────────────────────
    def register_mission(self, mission: MissionRecord) -> None:
        self._active_missions[mission.mission_id] = mission
        self._total_missions_executed += 1
        logger.info(f"[MissionControlCenter] Mission registered → {mission.mission_id} | {mission.mission_type} @ {mission.region}")

    def update_mission_status(self, mission_id: str, status: str) -> None:
        if mission_id in self._active_missions:
            self._active_missions[mission_id].status = status

    def get_mission(self, mission_id: str) -> Optional[MissionRecord]:
        return self._active_missions.get(mission_id)

    def list_missions(self) -> list[MissionRecord]:
        return list(self._active_missions.values())

    # ── Event log ────────────────────────────────────────────────────────────
    def log_event(self, event: EventRecord) -> None:
        self._event_log.append(event)
        self._total_events_fired += 1

    def get_event_log(self) -> list[EventRecord]:
        return list(reversed(self._event_log))

    # ── System statistics ────────────────────────────────────────────────────
    def get_statistics(self) -> dict[str, Any]:
        active = sum(1 for m in self._active_missions.values() if m.status == "ACTIVE")
        completed = sum(1 for m in self._active_missions.values() if m.status == "COMPLETED")
        idle_drones = sum(1 for d in self._registered_drones.values() if d.status == "IDLE")
        active_drones = sum(1 for d in self._registered_drones.values() if d.status == "ACTIVE")

        return {
            "total_missions": self._total_missions_executed,
            "active_missions": active,
            "completed_missions": completed,
            "total_drones": len(self._registered_drones),
            "idle_drones": idle_drones,
            "active_drones": active_drones,
            "total_events_fired": self._total_events_fired,
        }

    # ── Convenience ──────────────────────────────────────────────────────────
    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (
            f"<MissionControlCenter missions={stats['total_missions']} "
            f"drones={stats['total_drones']} events={stats['total_events_fired']}>"
        )
