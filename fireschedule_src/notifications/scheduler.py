"""Reminder Scheduler - Background event reminder checker."""

import logging
from datetime import datetime, timedelta
from typing import Set

from fireschedule_src.notifications.service import NotificationService
from fireschedule_src.notifications.config import ReminderConfig
from fireschedule_src.storage.markdown import MarkdownStorage
from fireschedule_src.models.events import Category

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Checks for upcoming events and sends notifications."""

    def __init__(self, config: ReminderConfig):
        self.config = config
        self.notification_service = NotificationService()
        self.storage = MarkdownStorage()
        self.notified_events: Set[str] = set()

    def check_and_notify(self) -> int:
        """
        Check for events needing reminders and send notifications.
        
        Returns:
            Number of notifications sent
        """
        if not self.config.enabled:
            return 0

        if not self.notification_service.is_available():
            logger.warning("Notification service not available")
            return 0

        events = []
        for category in [Category.SCHOOL, Category.LEARNING, Category.EXERCISE, Category.SOCIAL]:
            category_events = self.storage.list_events(category)
            events.extend(category_events)
        
        notifications_sent = 0
        now = datetime.now()

        for event in events:
            if event.completed:
                continue

            if not event.time:
                continue

            event_datetime = self._parse_event_datetime(event.date, event.time)
            if not event_datetime:
                continue

            minutes_until = (event_datetime - now).total_seconds() / 60

            if minutes_until <= self.config.default_minutes_before and minutes_until > 0:
                if event.id not in self.notified_events:
                    self.notification_service.send_notification(
                        title=f"Upcoming: {event.title}",
                        message=f"Starts in {int(minutes_until)} minutes",
                        sound=self.config.notification_sound
                    )
                    self.notified_events.add(event.id)
                    notifications_sent += 1
                    logger.info(f"Sent reminder for event: {event.id}")

        return notifications_sent

    def send_daily_summary(self) -> int:
        """
        Send daily summary of upcoming events.
        
        Returns:
            Number of events in summary
        """
        if not self.config.daily_summary_enabled:
            return 0

        if not self.notification_service.is_available():
            return 0

        events = []
        for category in [Category.SCHOOL, Category.LEARNING, Category.EXERCISE, Category.SOCIAL]:
            category_events = self.storage.list_events(category)
            events.extend(category_events)
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        upcoming = []
        for event in events:
            if event.completed:
                continue
            try:
                event_date = datetime.strptime(event.date, "%Y-%m-%d").date()
                if today <= event_date < tomorrow:
                    upcoming.append(event)
            except ValueError:
                continue

        if upcoming:
            event_list = "\n".join(f"  - {e.title} ({e.time or 'TBD'})" for e in upcoming)
            message = f"You have {len(upcoming)} event(s) tomorrow:\n{event_list}"
            
            self.notification_service.send_notification(
                title="FireSchedule Daily Summary",
                message=message,
                sound=self.config.notification_sound
            )

        return len(upcoming)

    def _parse_event_datetime(self, date_str: str, time_str: str) -> datetime:
        """Parse event date and time strings to datetime."""
        try:
            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return None

    def clear_notified(self):
        """Clear the set of notified events."""
        self.notified_events.clear()
