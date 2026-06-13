from datetime import datetime
from typing import Optional

from domain.entities.mission import MissionEntity
from domain.repositories.mission_repository import MissionRepository, MissionCreateData
from missions.models import Mission, MissionEvent
from core.enums import MissionStatus


class DjangoMissionRepository(MissionRepository):

    def create(self, data: MissionCreateData) -> MissionEntity:
        m = Mission.objects.create(
            name=data.name,
            mission_type=data.mission_type,
            region=data.region,
            priority=data.priority,
            route_strategy=data.route_strategy,
            assigned_drone_id=data.drone_id,
            status=MissionStatus.ACTIVE,
            estimated_duration_min=data.estimated_duration_min,
            distance_km=data.distance_km,
            battery_consumption_pct=data.battery_consumption_pct,
            weather_risk_score=data.weather_risk_score,
            waypoints=data.waypoints,
            route_notes=data.route_notes,
            started_at=datetime.now(),
        )
        return self._to_entity(m)

    def get_by_id(self, mission_id: str) -> Optional[MissionEntity]:
        try:
            return self._to_entity(Mission.objects.get(id=mission_id))
        except Mission.DoesNotExist:
            return None

    def list_all(self) -> list[MissionEntity]:
        return [self._to_entity(m) for m in Mission.objects.all()]

    def log_event(self, mission_id: str, event_type: str, message: str, severity: str) -> None:
        MissionEvent.objects.create(
            mission_id=mission_id,
            event_type=event_type,
            message=message,
            severity=severity,
        )

    def update_status(self, mission_id: str, status: str, completed_at=None) -> None:
        kwargs = {"status": status}
        if completed_at is not None:
            kwargs["completed_at"] = completed_at
        Mission.objects.filter(id=mission_id).update(**kwargs)

    @staticmethod
    def _to_entity(m: Mission) -> MissionEntity:
        return MissionEntity(
            id=str(m.id),
            name=m.name,
            mission_type=m.mission_type,
            region=m.region,
            priority=m.priority,
            route_strategy=m.route_strategy,
            status=m.status,
            assigned_drone_id=m.assigned_drone_id,
            estimated_duration_min=m.estimated_duration_min,
            distance_km=m.distance_km,
            battery_consumption_pct=m.battery_consumption_pct,
            weather_risk_score=m.weather_risk_score,
            waypoints=m.waypoints or [],
            route_notes=m.route_notes or "",
        )
