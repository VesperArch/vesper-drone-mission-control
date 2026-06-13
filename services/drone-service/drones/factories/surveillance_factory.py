from .base_factory import DroneFactory, DroneConfig
from core.enums import DroneType


class SurveillanceDroneFactory(DroneFactory):
    """
    Concrete Factory: produces high-altitude, long-endurance surveillance drones.
    Optimised for wide-area monitoring at the expense of payload capacity.
    """

    drone_type = DroneType.SURVEILLANCE

    def create_drone(self) -> DroneConfig:
        return DroneConfig(
            model="Vesper-S400 Sentinel",
            drone_type=DroneType.SURVEILLANCE,
            speed_kmh=95.0,
            battery_capacity_wh=420.0,
            altitude_limit_m=400.0,
            payload_kg=0.5,
            range_km=60.0,
            description=(
                "Long-endurance surveillance platform with 4K optical zoom and "
                "thermal imaging. Designed for persistent area monitoring."
            ),
        )
