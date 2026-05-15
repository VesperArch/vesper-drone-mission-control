from .base_factory import DroneFactory, DroneConfig
from core.enums import DroneType


class EmergencyDroneFactory(DroneFactory):
    """
    Concrete Factory: produces fast-response emergency drones.
    Prioritises speed and maneuverability over range and payload.
    """

    drone_type = DroneType.EMERGENCY

    def create_drone(self) -> DroneConfig:
        return DroneConfig(
            model="Vesper-E200 Raptor",
            drone_type=DroneType.EMERGENCY,
            speed_kmh=140.0,
            battery_capacity_wh=380.0,
            altitude_limit_m=200.0,
            payload_kg=2.0,
            range_km=35.0,
            description=(
                "High-speed emergency response drone equipped with siren array, "
                "searchlight, and first-aid drop capability."
            ),
        )
