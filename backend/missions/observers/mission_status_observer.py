"""
DESIGN PATTERN: Observer — Concrete Observer #3
────────────────────────────────────────────────
MissionStatusObserver keeps the Django ORM model and the Singleton registry
in sync when mission lifecycle events are received. It is the bridge between
the domain event system and the persistence layer.
"""

from loguru import logger
from core.events import MissionObserverInterface, MissionEventData
from core.singleton import MissionControlCenter
from core.enums import MissionStatus, DroneStatus


class MissionStatusObserver(MissionObserverInterface):
    """
    Updates both the in-memory Singleton registry and the DB mission record
    whenever a terminal lifecycle event arrives.
    """

    def update(self, event: MissionEventData) -> None:
        control = MissionControlCenter.get_instance()

        if event.event_type == "MISSION_STARTED":
            control.update_mission_status(event.mission_id, MissionStatus.ACTIVE)
            if event.drone_id:
                control.update_drone_status(event.drone_id, DroneStatus.ACTIVE)
            logger.info(f"[StatusObserver] Mission {event.mission_id[:8]}… → ACTIVE")

        elif event.event_type == "MISSION_COMPLETED":
            control.update_mission_status(event.mission_id, MissionStatus.COMPLETED)
            if event.drone_id:
                control.update_drone_status(event.drone_id, DroneStatus.IDLE, battery_level=45.0)
            logger.success(f"[StatusObserver] Mission {event.mission_id[:8]}… → COMPLETED")

        elif event.event_type in ("MISSION_FAILED", "RETURN_TO_BASE"):
            control.update_mission_status(event.mission_id, MissionStatus.FAILED)
            if event.drone_id:
                control.update_drone_status(event.drone_id, DroneStatus.RETURNING)
            logger.warning(f"[StatusObserver] Mission {event.mission_id[:8]}… → FAILED/RETURNING")

        # Always log the event to the singleton's event log
        from core.singleton.mission_control_center import EventRecord
        control.log_event(EventRecord(
            mission_id=event.mission_id,
            event_type=event.event_type,
            message=event.message,
            timestamp=event.timestamp,
        ))
