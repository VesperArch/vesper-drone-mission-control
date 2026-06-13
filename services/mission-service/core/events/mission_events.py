"""
DESIGN PATTERN: Observer
────────────────────────
Mission operations are event-driven. When significant things happen during a
mission (low battery, bad weather, completion), multiple independent subsystems
must react — without those subsystems being tightly coupled to each other.

The Observer pattern solves this via two abstractions:

  MissionSubject   – the thing being watched; holds an observer list and fires
                     notify() when an event occurs.
  MissionObserverInterface – the contract any listener must implement (update).

Concrete observers (LoggerObserver, AlertObserver, MissionStatusObserver) are
attached at mission start via the Facade and are completely unaware of each
other. Adding a new observer never modifies the subject.

Why Observer here?
  A mission lifecycle can trigger 6+ distinct event types. Without Observer, the
  mission service would need direct calls to logging, alerting, and status update
  code — violating both Open/Closed and Single Responsibility principles.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING


@dataclass
class MissionEventData:
    """Value object carried by every observer notification."""

    mission_id: str
    event_type: str          # maps to EventType enum value
    message: str
    drone_id: str = ""
    severity: str = "INFO"   # INFO | WARNING | ALERT | SUCCESS
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)


class MissionObserverInterface(ABC):
    """
    Observer contract.
    All concrete observers must implement update() to react to mission events.
    """

    @abstractmethod
    def update(self, event: MissionEventData) -> None:
        """React to an event published by a MissionSubject."""
        ...


class MissionSubject:
    """
    Subject (Observable) in the Observer pattern.

    Maintains a list of attached observers and notifies all of them when
    an event occurs. Observers can be added/removed at any time.
    """

    def __init__(self) -> None:
        self._observers: list[MissionObserverInterface] = []

    # ── Observer management ──────────────────────────────────────────────────
    def attach(self, observer: MissionObserverInterface) -> None:
        """Register an observer to receive future notifications."""
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: MissionObserverInterface) -> None:
        """Unregister an observer; safe to call even if not attached."""
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    # ── Notification ─────────────────────────────────────────────────────────
    def notify(self, event: MissionEventData) -> None:
        """
        Broadcast event to every registered observer.
        Each observer reacts independently — ordering is insertion order.
        """
        for observer in self._observers:
            observer.update(event)

    @property
    def observer_count(self) -> int:
        return len(self._observers)
