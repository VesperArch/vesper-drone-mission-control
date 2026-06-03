Feature: Mission Lifecycle
  As a mission operator
  I want to start and track drone missions
  So that I can coordinate emergency response operations

  Scenario: Start a mission with an available drone
    Given a drone with status "IDLE" exists in the database
    When I submit a mission creation request for that drone
    Then the mission status should be "ACTIVE"
    And the drone status should change to "ACTIVE"

  Scenario: Cannot start a mission with a busy drone
    Given a drone with status "ACTIVE" exists in the database
    When I submit a mission creation request for that drone
    Then the response should contain an error message
