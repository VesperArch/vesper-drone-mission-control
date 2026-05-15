from enum import StrEnum


class DroneType(StrEnum):
    SURVEILLANCE = "SURVEILLANCE"
    EMERGENCY = "EMERGENCY"
    DELIVERY = "DELIVERY"


class DroneStatus(StrEnum):
    IDLE = "IDLE"
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    CHARGING = "CHARGING"
    RETURNING = "RETURNING"
