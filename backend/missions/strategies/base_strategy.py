"""
DESIGN PATTERN: Strategy
─────────────────────────
Route calculation is a behaviour that varies independently from the rest of the
mission. Different missions call for different trade-offs: speed vs safety vs
battery life. The Strategy pattern encapsulates each variant as an interchangeable
object behind a shared interface, so the context (the mission service / facade)
doesn't need to know which algorithm is in use.

Structure:
  RouteStrategy (abstract)          ← algorithm interface
    ├── FastestRouteStrategy        ← minimises travel time
    ├── SafeRouteStrategy           ← minimises weather/obstacle risk
    └── BatterySavingStrategy       ← minimises energy consumption

RouteResult is the shared output type — regardless of which strategy ran.

Why Strategy here?
  Adding a fourth strategy (e.g. StealthRouteStrategy) requires zero changes to
  the mission service. The Facade simply passes the new strategy object. Runtime
  switching (changing strategy mid-mission) is also trivially supported.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RouteResult:
    """Value object returned by every strategy implementation."""

    strategy_used: str
    estimated_duration_min: float
    distance_km: float
    battery_consumption_pct: float
    weather_risk_score: float       # 0.0 (clear) – 1.0 (extreme)
    waypoints: list[str]
    notes: str


class RouteStrategy(ABC):
    """
    Strategy interface: declares calculate_route() that all concrete strategies
    must implement.  The method is intentionally side-effect-free — it returns
    a RouteResult without mutating any state.
    """

    @abstractmethod
    def calculate_route(
        self,
        origin: str,
        destination: str,
        drone_speed_kmh: float,
        drone_range_km: float,
    ) -> RouteResult:
        """
        Compute a route from origin to destination for the given drone specs.
        Returns a RouteResult with time, distance, battery, and risk estimates.
        """
        ...

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Human-readable name used in logs and API responses."""
        ...
