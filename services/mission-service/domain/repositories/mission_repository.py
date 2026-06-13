from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from domain.entities.mission import MissionEntity


@dataclass
class MissionCreateData:
    name: str
    mission_type: str
    region: str
    priority: str
    route_strategy: str
    drone_id: str
    estimated_duration_min: float
    distance_km: float
    battery_consumption_pct: float
    weather_risk_score: float
    waypoints: list = field(default_factory=list)
    route_notes: str = ""


class MissionRepository(ABC):
    @abstractmethod
    def create(self, data: MissionCreateData) -> MissionEntity: ...

    @abstractmethod
    def get_by_id(self, mission_id: str) -> Optional[MissionEntity]: ...

    @abstractmethod
    def list_all(self) -> list[MissionEntity]: ...

    @abstractmethod
    def log_event(self, mission_id: str, event_type: str, message: str, severity: str) -> None: ...

    @abstractmethod
    def update_status(self, mission_id: str, status: str, completed_at=None) -> None: ...
