import pytest
from pytest_bdd import scenarios, when, then, parsers

from drones.factories.surveillance_factory import SurveillanceDroneFactory
from drones.factories.emergency_factory import EmergencyDroneFactory
from drones.factories.delivery_factory import DeliveryDroneFactory

scenarios("../../features/drone_factory.feature")


@when("I build a drone using the surveillance factory", target_fixture="drone_config")
def build_surveillance():
    return SurveillanceDroneFactory().build()


@when("I build a drone using the emergency factory", target_fixture="drone_config")
def build_emergency():
    return EmergencyDroneFactory().build()


@when("I build a drone using the delivery factory", target_fixture="drone_config")
def build_delivery():
    return DeliveryDroneFactory().build()


@then(parsers.parse('the drone type should be "{drone_type}"'))
def check_drone_type(drone_config, drone_type):
    assert drone_config.drone_type == drone_type


@then(parsers.parse("the drone range should be {range_km:g} km"))
def check_drone_range(drone_config, range_km):
    assert drone_config.range_km == pytest.approx(range_km)


@then(parsers.parse("the drone payload should be {payload:g} kg"))
def check_drone_payload(drone_config, payload):
    assert drone_config.payload_kg == pytest.approx(payload)


@then(parsers.parse("the drone speed should be {speed:g} km/h"))
def check_drone_speed(drone_config, speed):
    assert drone_config.speed_kmh == pytest.approx(speed)
