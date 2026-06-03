Feature: Alert Observer
  As a safety system
  I want to filter mission events by severity
  So that operators are alerted only for critical situations

  Background:
    Given the alert observer is monitoring a mission

  Scenario: Critical event triggers an alert
    When a LOW_BATTERY event occurs
    Then the alert buffer should contain 1 alert
    And the alert should reference the correct mission

  Scenario: Bad weather event triggers an alert
    When a BAD_WEATHER event occurs
    Then the alert buffer should contain 1 alert

  Scenario: Informational event does not trigger an alert
    When a MISSION_STARTED event occurs
    Then the alert buffer should be empty

  Scenario: Clearing alerts resets the buffer
    When a LOW_BATTERY event occurs
    And I clear the alert buffer
    Then the alert buffer should be empty
