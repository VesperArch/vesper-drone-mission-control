Feature: Drone Factory
  As a system administrator
  I want to create drones using predefined factories
  So that each drone type has the correct specifications

  Scenario: Creating a surveillance drone
    When I build a drone using the surveillance factory
    Then the drone type should be "SURVEILLANCE"
    And the drone range should be 60 km
    And the drone payload should be 0.5 kg

  Scenario: Creating an emergency drone
    When I build a drone using the emergency factory
    Then the drone type should be "EMERGENCY"
    And the drone speed should be 140 km/h

  Scenario: Creating a delivery drone
    When I build a drone using the delivery factory
    Then the drone type should be "DELIVERY"
    And the drone payload should be 8.0 kg
