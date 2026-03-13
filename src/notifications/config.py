"""Reminder Configuration."""

from pydantic import BaseModel
from typing import Optional


class ReminderConfig(BaseModel):
    """Configuration for reminder/notification system."""
    
    enabled: bool = True
    default_minutes_before: int = 15
    daily_summary_enabled: bool = False
    daily_summary_time: str = "08:00"
    notification_sound: bool = True
    
    def to_dict(self) -> dict:
        """Convert to dictionary for YAML."""
        return {
            "enabled": self.enabled,
            "default_minutes_before": self.default_minutes_before,
            "daily_summary_enabled": self.daily_summary_enabled,
            "daily_summary_time": self.daily_summary_time,
            "notification_sound": self.notification_sound,
        }
    
    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "ReminderConfig":
        """Create from dictionary."""
        if not data:
            return cls()
        return cls(**data)
