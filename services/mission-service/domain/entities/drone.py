from dataclasses import dataclass


@dataclass
class DroneEntity:
    id: str
    name: str
    drone_type: str
    status: str
    speed_kmh: float
    range_km: float
    battery_level: float
