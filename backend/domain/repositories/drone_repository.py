from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.drone import DroneEntity


class DroneRepository(ABC):
    @abstractmethod
    def get_by_id(self, drone_id: str) -> Optional[DroneEntity]: ...

    @abstractmethod
    def save(self, drone: DroneEntity) -> None: ...

    @abstractmethod
    def list_all(self) -> list[DroneEntity]: ...
