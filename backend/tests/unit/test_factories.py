import pytest
from drones.factories.surveillance_factory import SurveillanceDroneFactory
from drones.factories.emergency_factory import EmergencyDroneFactory
from drones.factories.delivery_factory import DeliveryDroneFactory
from drones.factories.base_factory import DroneConfig


class TestSurveillanceDroneFactory:
    def setup_method(self):
        self.factory = SurveillanceDroneFactory()

    def test_build_returns_drone_config(self):
        config = self.factory.build()
        assert isinstance(config, DroneConfig)

    def test_drone_type_is_surveillance(self):
        config = self.factory.build()
        assert config.drone_type == "SURVEILLANCE"

    def test_speed(self):
        config = self.factory.build()
        assert config.speed_kmh == 95.0

    def test_range(self):
        config = self.factory.build()
        assert config.range_km == 60.0

    def test_payload(self):
        config = self.factory.build()
        assert config.payload_kg == 0.5

    def test_altitude_limit(self):
        config = self.factory.build()
        assert config.altitude_limit_m == 400.0

    def test_has_model_name(self):
        config = self.factory.build()
        assert config.model and len(config.model) > 0

    def test_build_is_idempotent(self):
        config1 = self.factory.build()
        config2 = self.factory.build()
        assert config1.drone_type == config2.drone_type
        assert config1.speed_kmh == config2.speed_kmh
        assert config1.range_km == config2.range_km


class TestEmergencyDroneFactory:
    def setup_method(self):
        self.factory = EmergencyDroneFactory()

    def test_build_returns_drone_config(self):
        config = self.factory.build()
        assert isinstance(config, DroneConfig)

    def test_drone_type_is_emergency(self):
        config = self.factory.build()
        assert config.drone_type == "EMERGENCY"

    def test_speed_is_fastest(self):
        config = self.factory.build()
        assert config.speed_kmh == 140.0

    def test_range(self):
        config = self.factory.build()
        assert config.range_km == 35.0

    def test_payload(self):
        config = self.factory.build()
        assert config.payload_kg == 2.0

    def test_altitude_limit(self):
        config = self.factory.build()
        assert config.altitude_limit_m == 200.0

    def test_build_is_idempotent(self):
        config1 = self.factory.build()
        config2 = self.factory.build()
        assert config1.speed_kmh == config2.speed_kmh


class TestDeliveryDroneFactory:
    def setup_method(self):
        self.factory = DeliveryDroneFactory()

    def test_build_returns_drone_config(self):
        config = self.factory.build()
        assert isinstance(config, DroneConfig)

    def test_drone_type_is_delivery(self):
        config = self.factory.build()
        assert config.drone_type == "DELIVERY"

    def test_speed_is_slowest(self):
        config = self.factory.build()
        assert config.speed_kmh == 65.0

    def test_range(self):
        config = self.factory.build()
        assert config.range_km == 25.0

    def test_payload_is_largest(self):
        config = self.factory.build()
        assert config.payload_kg == 8.0

    def test_altitude_limit(self):
        config = self.factory.build()
        assert config.altitude_limit_m == 150.0

    def test_battery_capacity_is_largest(self):
        delivery = self.factory.build()
        surveillance = SurveillanceDroneFactory().build()
        emergency = EmergencyDroneFactory().build()
        assert delivery.battery_capacity_wh > surveillance.battery_capacity_wh
        assert delivery.battery_capacity_wh > emergency.battery_capacity_wh

    def test_build_is_idempotent(self):
        config1 = self.factory.build()
        config2 = self.factory.build()
        assert config1.payload_kg == config2.payload_kg
