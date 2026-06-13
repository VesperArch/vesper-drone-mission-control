"""
DESIGN PATTERN: Factory Method
───────────────────────────────
Drone creation is delegated to specialised factory subclasses rather than being
hard-coded in a single "if drone_type == X" block. This decouples the calling
code from the concrete drone classes and makes it trivial to introduce a new
drone variant (e.g. MedicalDrone) without touching existing code.

Structure:
  DroneFactory (abstract)             ← defines the factory method contract
    ├── SurveillanceDroneFactory      ← creates surveillance drones
    ├── EmergencyDroneFactory         ← creates emergency-response drones
    └── DeliveryDroneFactory          ← creates supply-delivery drones

DroneConfig is the product interface — a pure dataclass that carries all
attributes a drone has. It is intentionally a value object with no behaviour;
behaviour lives in domain services.

Why Factory Method here?
  Each drone type has meaningfully different defaults (speed, payload, range).
  If those defaults changed (hardware upgrade), you touch exactly one factory.
  The polymorphic design also lets the Facade accept a factory without knowing
  which concrete variant it is.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class DroneConfig:
    """
    Product: the value object returned by every factory.
    Represents the immutable specification of a newly-created drone.
    """

    model: str
    drone_type: str           # maps to DroneType enum
    speed_kmh: float          # max horizontal speed
    battery_capacity_wh: float
    altitude_limit_m: float
    payload_kg: float
    range_km: float
    description: str


class DroneFactory(ABC):
    """
    Creator: declares the factory method that subclasses must implement.

    Also provides a shared convenience method register_with_db() that
    persists the drone after creation, keeping that concern out of the
    concrete factories.
    """

    # Subclasses declare the drone type they produce.
    drone_type: ClassVar[str]

    @abstractmethod
    def create_drone(self) -> DroneConfig:
        """
        Factory Method — override in each concrete factory to return
        a DroneConfig populated with type-specific defaults.
        """
        ...

    def build(self) -> DroneConfig:
        """
        Template wrapper around the factory method.
        Can be extended with common pre/post-creation logic.
        """
        config = self.create_drone()
        return config
