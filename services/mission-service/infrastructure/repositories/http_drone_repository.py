"""
MICROSERVICES + CLEAN ARCHITECTURE: HttpDroneRepository
────────────────────────────────────────────────────────
This is the KEY file that makes microservices work with Clean Architecture.

The DroneRepository ABC was defined in the domain layer.
In the monolith, DjangoDroneRepository implemented it via Django ORM.
Here, HttpDroneRepository implements the SAME interface via HTTP calls to
drone-service — without changing a single line in StartMissionUseCase or
DroneMissionFacade.

Dependency rule:
  domain/  ← application/  ← infrastructure/  (this file)
                                ↓ HTTP ↓
                          drone-service:8001

The use case doesn't know or care whether drones come from a local ORM
or a remote service — it just calls get_by_id() and save().
"""

from __future__ import annotations

from typing import Optional

import requests
from django.conf import settings
from loguru import logger

from domain.entities.drone import DroneEntity
from domain.repositories.drone_repository import DroneRepository


class DroneServiceError(Exception):
    pass


class HttpDroneRepository(DroneRepository):
    """
    Implements DroneRepository by calling drone-service over HTTP.
    Swapped in place of DjangoDroneRepository — zero changes to use cases.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self._base = (base_url or getattr(settings, "DRONE_SERVICE_URL", "http://drone-service:8001")).rstrip("/")

    def get_by_id(self, drone_id: str) -> Optional[DroneEntity]:
        try:
            resp = requests.get(f"{self._base}/api/drones/{drone_id}/", timeout=5)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return self._to_entity(resp.json())
        except requests.RequestException as exc:
            logger.error(f"[HttpDroneRepository] GET drone/{drone_id} failed: {exc}")
            raise DroneServiceError(f"drone-service unavailable: {exc}") from exc

    def save(self, drone: DroneEntity) -> None:
        """PATCH drone-service to update status and battery after mission events."""
        try:
            resp = requests.patch(
                f"{self._base}/api/drones/{drone.id}/status/",
                json={"status": drone.status, "battery_level": drone.battery_level},
                timeout=5,
            )
            resp.raise_for_status()
        except requests.RequestException as exc:
            logger.error(f"[HttpDroneRepository] PATCH drone/{drone.id} failed: {exc}")
            raise DroneServiceError(f"drone-service unavailable: {exc}") from exc

    def list_all(self) -> list[DroneEntity]:
        try:
            resp = requests.get(f"{self._base}/api/drones/", timeout=5)
            resp.raise_for_status()
            return [self._to_entity(d) for d in resp.json()]
        except requests.RequestException as exc:
            logger.error(f"[HttpDroneRepository] GET drones/ failed: {exc}")
            raise DroneServiceError(f"drone-service unavailable: {exc}") from exc

    @staticmethod
    def _to_entity(data: dict) -> DroneEntity:
        return DroneEntity(
            id=str(data["id"]),
            name=data["name"],
            drone_type=data["drone_type"],
            status=data["status"],
            speed_kmh=float(data["speed_kmh"]),
            range_km=float(data["range_km"]),
            battery_level=float(data["battery_level"]),
        )
