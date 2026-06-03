import pytest
from missions.strategies.fastest_route import FastestRouteStrategy
from missions.strategies.safe_route import SafeRouteStrategy
from missions.strategies.battery_saving import BatterySavingStrategy
from missions.strategies.base_strategy import RouteResult


SPEED = 95.0
RANGE = 60.0
ORIGIN = "Centro"
DEST = "Itaipuaçu"
DIRECT_DISTANCE = 18.0  # known from _REGION_DISTANCES map


class TestFastestRouteStrategy:
    def setup_method(self):
        self.strategy = FastestRouteStrategy()

    def test_strategy_name(self):
        assert self.strategy.strategy_name == "FASTEST"

    def test_returns_route_result(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert isinstance(result, RouteResult)

    def test_weather_risk_is_high(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.weather_risk_score == 0.45

    def test_waypoints_are_only_origin_and_destination(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.waypoints == [ORIGIN, DEST]

    def test_battery_formula(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        expected = round((DIRECT_DISTANCE / RANGE) * 100 * 1.15, 1)
        assert result.battery_consumption_pct == expected

    def test_duration_formula(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        expected = round((DIRECT_DISTANCE / SPEED) * 60, 1)
        assert result.estimated_duration_min == expected

    def test_distance_matches_region_map(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.distance_km == DIRECT_DISTANCE

    def test_unmapped_pair_uses_default_distance(self):
        result = self.strategy.calculate_route("São José", "Cordeirinho", SPEED, RANGE)
        assert result.distance_km == 20.0

    def test_strategy_used_field(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.strategy_used == "FASTEST"


class TestSafeRouteStrategy:
    def setup_method(self):
        self.strategy = SafeRouteStrategy()

    def test_strategy_name(self):
        assert self.strategy.strategy_name == "SAFE"

    def test_returns_route_result(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert isinstance(result, RouteResult)

    def test_weather_risk_is_low(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.weather_risk_score == 0.10

    def test_weather_risk_below_020(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.weather_risk_score < 0.20

    def test_distance_is_longer_than_direct(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.distance_km > DIRECT_DISTANCE

    def test_distance_adds_25_percent_detour(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        expected = round(18.0 * 1.25, 1)
        assert result.distance_km == expected

    def test_has_intermediate_waypoint_when_route_allows_it(self):
        # SafeRoute adds an intermediate waypoint when it's distinct from origin/destination.
        # Use Inoã→São José so "Ponta Negra" intermediate doesn't collide with either endpoint.
        result = self.strategy.calculate_route("Inoã", "São José", SPEED, RANGE)
        assert len(result.waypoints) == 3

    def test_battery_formula(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        distance = 18.0 * 1.25
        expected = round((distance / RANGE) * 100 * 1.05, 1)
        assert result.battery_consumption_pct == expected

    def test_strategy_used_field(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.strategy_used == "SAFE"


class TestBatterySavingStrategy:
    def setup_method(self):
        self.strategy = BatterySavingStrategy()

    def test_strategy_name(self):
        assert self.strategy.strategy_name == "BATTERY_SAVING"

    def test_returns_route_result(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert isinstance(result, RouteResult)

    def test_weather_risk_is_moderate(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.weather_risk_score == 0.25

    def test_cordeirinho_in_waypoints(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert "Cordeirinho" in result.waypoints

    def test_distance_adds_10_percent(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        expected = round(18.0 * 1.10, 1)
        assert result.distance_km == expected

    def test_battery_saves_compared_to_fastest(self):
        fastest = FastestRouteStrategy()
        battery_saving = self.strategy
        fast_result = fastest.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        save_result = battery_saving.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert save_result.battery_consumption_pct < fast_result.battery_consumption_pct

    def test_battery_formula(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        distance = 18.0 * 1.10
        expected = round((distance / RANGE) * 100 * 0.72, 1)
        assert result.battery_consumption_pct == expected

    def test_duration_uses_reduced_speed(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        distance = 18.0 * 1.10
        effective_speed = SPEED * 0.65
        expected = round((distance / effective_speed) * 60, 1)
        assert result.estimated_duration_min == expected

    def test_strategy_used_field(self):
        result = self.strategy.calculate_route(ORIGIN, DEST, SPEED, RANGE)
        assert result.strategy_used == "BATTERY_SAVING"
