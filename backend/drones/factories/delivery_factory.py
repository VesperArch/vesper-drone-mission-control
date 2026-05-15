from .base_factory import DroneFactory, DroneConfig
from core.enums import DroneType


class DeliveryDroneFactory(DroneFactory):
    """
    Concrete Factory: produces heavy-lift delivery drones.
    Prioritises payload capacity and stable flight at moderate speed.
    """

    drone_type = DroneType.DELIVERY

    def create_drone(self) -> DroneConfig:
        return DroneConfig(
            model="Vesper-D800 Carrier",
            drone_type=DroneType.DELIVERY,
            speed_kmh=65.0,
            battery_capacity_wh=560.0,
            altitude_limit_m=150.0,
            payload_kg=8.0,
            range_km=25.0,
            description=(
                "Heavy-lift supply delivery platform with precision landing system. "
                "Carries medical kits, food packages, and emergency equipment."
            ),
        )
