Feature: Route Strategy Selection
  As a mission operator
  I want to choose a route strategy
  So that I can balance speed, safety, and battery life

  Background:
    Given a drone with speed 95 km/h and range 60 km

  Scenario: Fastest route prioritizes travel time
    When I calculate the route using the FASTEST strategy from "Centro" to "Itaipuaçu"
    Then the weather risk score should be 0.45
    And the waypoints should contain only origin and destination

  Scenario: Safe route avoids weather risk
    When I calculate the route using the SAFE strategy from "Centro" to "Itaipuaçu"
    Then the weather risk score should be less than 0.20
    And the route distance should be longer than the direct distance

  Scenario: Battery saving route reduces energy consumption
    When I calculate the route using the BATTERY_SAVING strategy from "Centro" to "Itaipuaçu"
    Then the battery consumption should be less than with the FASTEST strategy
