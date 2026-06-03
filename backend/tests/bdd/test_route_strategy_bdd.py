import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from missions.strategies.fastest_route import FastestRouteStrategy
from missions.strategies.safe_route import SafeRouteStrategy
from missions.strategies.battery_saving import BatterySavingStrategy

scenarios("../../features/route_strategy.feature")

DIRECT_DISTANCE = 18.0  # Centro → Itaipuaçu


@pytest.fixture
def context():
    return {}


@given(parsers.parse("a drone with speed {speed:g} km/h and range {range_km:g} km"), target_fixture="drone_specs")
def drone_specs(speed, range_km):
    return {"speed": float(speed), "range": float(range_km)}


@when(parsers.parse('I calculate the route using the FASTEST strategy from "{origin}" to "{destination}"'), target_fixture="fastest_result")
def calc_fastest(drone_specs, origin, destination):
    strategy = FastestRouteStrategy()
    return strategy.calculate_route(origin, destination, drone_specs["speed"], drone_specs["range"])


@when(parsers.parse('I calculate the route using the SAFE strategy from "{origin}" to "{destination}"'), target_fixture="safe_result")
def calc_safe(drone_specs, origin, destination):
    strategy = SafeRouteStrategy()
    return strategy.calculate_route(origin, destination, drone_specs["speed"], drone_specs["range"])


@when(parsers.parse('I calculate the route using the BATTERY_SAVING strategy from "{origin}" to "{destination}"'), target_fixture="battery_result")
def calc_battery(drone_specs, origin, destination):
    strategy = BatterySavingStrategy()
    return strategy.calculate_route(origin, destination, drone_specs["speed"], drone_specs["range"])


@then(parsers.parse("the weather risk score should be {score:g}"))
def check_weather_risk(fastest_result, score):
    assert fastest_result.weather_risk_score == pytest.approx(score)


@then("the waypoints should contain only origin and destination")
def check_waypoints_direct(fastest_result):
    assert len(fastest_result.waypoints) == 2


@then(parsers.parse("the weather risk score should be less than {threshold:g}"))
def check_weather_risk_below(safe_result, threshold):
    assert safe_result.weather_risk_score < threshold


@then("the route distance should be longer than the direct distance")
def check_safe_longer(safe_result):
    assert safe_result.distance_km > DIRECT_DISTANCE


@then("the battery consumption should be less than with the FASTEST strategy")
def check_battery_saving(battery_result, drone_specs):
    fastest = FastestRouteStrategy()
    fast_result = fastest.calculate_route("Centro", "Itaipuaçu", drone_specs["speed"], drone_specs["range"])
    assert battery_result.battery_consumption_pct < fast_result.battery_consumption_pct
