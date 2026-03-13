"""Notification Service - Cross-platform desktop notifications."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationService:
    """Handles sending desktop notifications."""

    def __init__(self):
        self._notifier = None
        self._load_notifier()

    def _load_notifier(self):
        """Load the notification backend."""
        try:
            from plyer import notification
            self._notifier = notification
        except ImportError:
            logger.warning("plyer not available, notifications disabled")
            self._notifier = None

    def send_notification(
        self,
        title: str,
        message: str,
        sound: bool = True,
        app_icon: Optional[str] = None
    ) -> bool:
        """
        Send a desktop notification.
        
        Args:
            title: Notification title
            message: Notification message body
            sound: Whether to play a notification sound
            app_icon: Optional path to app icon
            
        Returns:
            True if notification sent successfully, False otherwise
        """
        if not self._notifier:
            logger.warning("Notification service not available")
            return False

        try:
            self._notifier.notify(
                title=title,
                message=message,
                app_name="FireSchedule",
                app_icon=app_icon,
                timeout=10,
            )
            logger.info(f"Notification sent: {title}")
            return True
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def is_available(self) -> bool:
        """Check if notification service is available."""
        return self._notifier is not None
