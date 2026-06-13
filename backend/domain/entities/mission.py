from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MissionEntity:
    id: str
    name: str
    mission_type: str
    region: str
    priority: str
    route_strategy: str
    status: str
    assigned_drone_id: Optional[str] = None
    estimated_duration_min: Optional[float] = None
    distance_km: Optional[float] = None
    battery_consumption_pct: Optional[float] = None
    weather_risk_score: Optional[float] = None
    waypoints: list = field(default_factory=list)
    route_notes: str = ""
