from .base_strategy import RouteStrategy, RouteResult
from core.enums import RouteStrategyType


class BatterySavingStrategy(RouteStrategy):
    """
    Concrete Strategy: fly at low altitude using prevailing sea breezes.
    Maximises range and battery efficiency at the expense of speed.
    """

    @property
    def strategy_name(self) -> str:
        return RouteStrategyType.BATTERY_SAVING

    def calculate_route(
        self,
        origin: str,
        destination: str,
        drone_speed_kmh: float,
        drone_range_km: float,
    ) -> RouteResult:
        base_distance = 18.0
        # Slightly longer path to exploit coastal wind assistance
        distance = base_distance * 1.10

        # Reduced speed maximises motor efficiency
        effective_speed = drone_speed_kmh * 0.65
        duration = (distance / effective_speed) * 60

        # Battery saving: ~30% less consumption
        battery_pct = min(100.0, (distance / drone_range_km) * 100 * 0.72)

        return RouteResult(
            strategy_used=self.strategy_name,
            estimated_duration_min=round(duration, 1),
            distance_km=round(distance, 1),
            battery_consumption_pct=round(battery_pct, 1),
            weather_risk_score=0.25,
            waypoints=[origin, "Cordeirinho", destination],
            notes="Coastal low-altitude route — exploits sea breeze for energy recovery.",
        )
