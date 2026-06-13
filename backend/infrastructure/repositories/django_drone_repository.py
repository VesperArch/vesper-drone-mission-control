from typing import Optional

from domain.entities.drone import DroneEntity
from domain.repositories.drone_repository import DroneRepository
from drones.models import Drone


class DjangoDroneRepository(DroneRepository):
    """
    Infrastructure: maps between DroneEntity (domain) and Drone (Django ORM).
    This is the ONLY place in the codebase allowed to import drones.models.
    """

    def get_by_id(self, drone_id: str) -> Optional[DroneEntity]:
        try:
            m = Drone.objects.get(id=drone_id)
            return self._to_entity(m)
        except Drone.DoesNotExist:
            return None

    def save(self, drone: DroneEntity) -> None:
        Drone.objects.filter(id=drone.id).update(
            status=drone.status,
            battery_level=drone.battery_level,
        )

    def list_all(self) -> list[DroneEntity]:
        return [self._to_entity(m) for m in Drone.objects.all()]

    @staticmethod
    def _to_entity(m: Drone) -> DroneEntity:
        return DroneEntity(
            id=str(m.id),
            name=m.name,
            drone_type=m.drone_type,
            status=m.status,
            speed_kmh=m.speed_kmh,
            range_km=m.range_km,
            battery_level=m.battery_level,
        )
