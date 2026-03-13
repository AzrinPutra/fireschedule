from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Category(str, Enum):
    SCHOOL = "school"
    LEARNING = "learning"
    EXERCISE = "exercise"
    SOCIAL = "social"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EventType(str, Enum):
    CLASS = "class"
    HOMEWORK = "homework"
    EXAM = "exam"
    SESSION = "session"
    PRACTICE = "practice"
    WORKOUT = "workout"
    SOCIAL = "social"
    REMINDER = "reminder"


class BaseEvent(BaseModel):
    id: str
    title: str
    category: Category
    event_type: EventType
    date: str  # ISO format YYYY-MM-DD
    time: Optional[str] = None  # HH:MM format
    duration_minutes: int = 60
    priority: Priority = Priority.MEDIUM
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        use_enum_values = True


class SchoolEvent(BaseEvent):
    category: Category = Category.SCHOOL
    event_type: EventType = EventType.CLASS
    location: Optional[str] = None
    teacher: Optional[str] = None
    homework_due: Optional[str] = None
    exam_date: Optional[str] = None


class LearningEvent(BaseEvent):
    category: Category = Category.LEARNING
    event_type: EventType = EventType.SESSION
    language: str  # Python, Bash, etc.
    topic: Optional[str] = None
    resources: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


class ExerciseEvent(BaseEvent):
    category: Category = Category.EXERCISE
    event_type: EventType = EventType.WORKOUT
    exercise_type: str  # Gym, Run, etc.
    location: Optional[str] = None
    sets: Optional[int] = None
    reps: Optional[int] = None


class SocialEvent(BaseEvent):
    category: Category = Category.SOCIAL
    event_type: EventType = EventType.SOCIAL
    location: Optional[str] = None
    people: list[str] = Field(default_factory=list)
    contact_reminder: bool = False


class Reminder(BaseModel):
    id: str
    event_id: str
    minutes_before: int = 15
    message: Optional[str] = None
    triggered: bool = False
