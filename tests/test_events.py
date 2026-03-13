import pytest
from datetime import datetime

from src.models.events import (
    Category,
    EventType,
    Priority,
    BaseEvent,
    LearningEvent,
)


class TestEvents:
    def test_base_event_creation(self):
        event = BaseEvent(
            id="test-001",
            title="Test Event",
            category=Category.LEARNING,
            event_type=EventType.SESSION,
            date="2026-03-13",
            time="10:00",
            duration_minutes=60,
        )
        assert event.id == "test-001"
        assert event.title == "Test Event"
        assert event.category == Category.LEARNING
        assert event.completed is False

    def test_learning_event(self):
        event = LearningEvent(
            id="learn-001",
            title="Python Practice",
            category=Category.LEARNING,
            event_type=EventType.SESSION,
            date="2026-03-14",
            time="14:00",
            duration_minutes=90,
            language="Python",
            topic="Data Structures",
        )
        assert event.language == "Python"
        assert event.topic == "Data Structures"

    def test_event_priority(self):
        event = BaseEvent(
            id="test-002",
            title="High Priority",
            category=Category.SCHOOL,
            event_type=EventType.EXAM,
            date="2026-03-15",
            priority=Priority.HIGH,
        )
        assert event.priority == Priority.HIGH
