from .base_strategy import RouteStrategy, RouteResult
from core.enums import RouteStrategyType

# Simulated region-to-region distances in km (Maricá geography approximation)
_REGION_DISTANCES: dict[tuple[str, str], float] = {
    ("Centro", "Itaipuaçu"): 18.0,
    ("Centro", "Ponta Negra"): 22.0,
    ("Centro", "Inoã"): 12.0,
    ("Centro", "São José"): 8.0,
    ("Centro", "Cordeirinho"): 15.0,
    ("Itaipuaçu", "Ponta Negra"): 6.0,
    ("Itaipuaçu", "Inoã"): 14.0,
    ("Ponta Negra", "Cordeirinho"): 9.0,
    ("Inoã", "São José"): 5.0,
}


def _distance(a: str, b: str) -> float:
    key = (a, b)
    if key in _REGION_DISTANCES:
        return _REGION_DISTANCES[key]
    rev = (b, a)
    if rev in _REGION_DISTANCES:
        return _REGION_DISTANCES[rev]
    return 20.0  # default for unmapped pairs


class FastestRouteStrategy(RouteStrategy):
    """
    Concrete Strategy: fly direct with maximum speed.
    Minimises travel time but ignores weather risk and battery efficiency.
    """

    @property
    def strategy_name(self) -> str:
        return RouteStrategyType.FASTEST

    def calculate_route(
        self,
        origin: str,
        destination: str,
        drone_speed_kmh: float,
        drone_range_km: float,
    ) -> RouteResult:
        distance = _distance(origin, destination)
        duration = (distance / drone_speed_kmh) * 60  # minutes

        # Direct path = higher battery draw (no thermal-assisted glide)
        battery_pct = min(100.0, (distance / drone_range_km) * 100 * 1.15)

        return RouteResult(
            strategy_used=self.strategy_name,
            estimated_duration_min=round(duration, 1),
            distance_km=round(distance, 1),
            battery_consumption_pct=round(battery_pct, 1),
            weather_risk_score=0.45,   # ignores weather avoidance
            waypoints=[origin, destination],
            notes="Direct high-speed route — weather hazards not avoided.",
        )
