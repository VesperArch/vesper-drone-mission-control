import pytest
from datetime import datetime
from unittest.mock import MagicMock

from core.events.mission_events import MissionSubject, MissionEventData, MissionObserverInterface


def make_event(event_type: str = "MISSION_STARTED") -> MissionEventData:
    return MissionEventData(
        mission_id="test-mission",
        event_type=event_type,
        message="Test",
        timestamp=datetime.now(),
    )


class TestMissionSubject:
    def setup_method(self):
        self.subject = MissionSubject()

    def test_starts_with_no_observers(self):
        assert self.subject.observer_count == 0

    def test_attach_increases_count(self):
        observer = MagicMock(spec=MissionObserverInterface)
        self.subject.attach(observer)
        assert self.subject.observer_count == 1

    def test_attach_duplicate_does_not_increase_count(self):
        observer = MagicMock(spec=MissionObserverInterface)
        self.subject.attach(observer)
        self.subject.attach(observer)
        assert self.subject.observer_count == 1

    def test_detach_decreases_count(self):
        observer = MagicMock(spec=MissionObserverInterface)
        self.subject.attach(observer)
        self.subject.detach(observer)
        assert self.subject.observer_count == 0

    def test_detach_unregistered_is_safe(self):
        observer = MagicMock(spec=MissionObserverInterface)
        self.subject.detach(observer)  # should not raise

    def test_notify_calls_all_observers(self):
        obs1 = MagicMock(spec=MissionObserverInterface)
        obs2 = MagicMock(spec=MissionObserverInterface)
        obs3 = MagicMock(spec=MissionObserverInterface)
        self.subject.attach(obs1)
        self.subject.attach(obs2)
        self.subject.attach(obs3)

        event = make_event()
        self.subject.notify(event)

        obs1.update.assert_called_once_with(event)
        obs2.update.assert_called_once_with(event)
        obs3.update.assert_called_once_with(event)

    def test_notify_with_no_observers_does_not_raise(self):
        self.subject.notify(make_event())  # should not raise

    def test_notify_calls_observer_with_correct_event(self):
        observer = MagicMock(spec=MissionObserverInterface)
        self.subject.attach(observer)
        event = make_event("LOW_BATTERY")
        self.subject.notify(event)
        observer.update.assert_called_once_with(event)

    def test_detached_observer_not_called(self):
        obs = MagicMock(spec=MissionObserverInterface)
        self.subject.attach(obs)
        self.subject.detach(obs)
        self.subject.notify(make_event())
        obs.update.assert_not_called()

    def test_multiple_attachments_notify_in_order(self):
        call_order = []
        obs1 = MagicMock(spec=MissionObserverInterface)
        obs2 = MagicMock(spec=MissionObserverInterface)
        obs1.update.side_effect = lambda e: call_order.append(1)
        obs2.update.side_effect = lambda e: call_order.append(2)
        self.subject.attach(obs1)
        self.subject.attach(obs2)
        self.subject.notify(make_event())
        assert call_order == [1, 2]
