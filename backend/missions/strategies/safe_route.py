from .base_strategy import RouteStrategy, RouteResult
from core.enums import RouteStrategyType


class SafeRouteStrategy(RouteStrategy):
    """
    Concrete Strategy: route avoids bad weather and obstacle corridors.
    Adds detour distance but dramatically lowers weather risk score.
    """

    @property
    def strategy_name(self) -> str:
        return RouteStrategyType.SAFE

    def calculate_route(
        self,
        origin: str,
        destination: str,
        drone_speed_kmh: float,
        drone_range_km: float,
    ) -> RouteResult:
        # Safe routes always pass through a cleared coastal corridor
        intermediate = "Ponta Negra" if "Itaipuaçu" not in (origin, destination) else "Centro"
        waypoints = [origin, intermediate, destination] if intermediate not in (origin, destination) else [origin, destination]

        # Detour adds ~25% to distance
        base_distance = 18.0
        distance = base_distance * 1.25
        duration = (distance / (drone_speed_kmh * 0.85)) * 60  # slower, cautious flight

        battery_pct = min(100.0, (distance / drone_range_km) * 100 * 1.05)

        return RouteResult(
            strategy_used=self.strategy_name,
            estimated_duration_min=round(duration, 1),
            distance_km=round(distance, 1),
            battery_consumption_pct=round(battery_pct, 1),
            weather_risk_score=0.10,   # actively avoids storm cells
            waypoints=waypoints,
            notes="Weather-safe corridor route via cleared airspace. Lower speed for obstacle avoidance.",
        )
