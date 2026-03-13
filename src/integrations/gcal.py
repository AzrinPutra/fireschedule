"""Google Calendar Integration Module.

Provides OAuth authentication and bi-directional sync with Google Calendar.
"""

import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

from src.models.events import (
    BaseEvent, Category, EventType, Priority
)
from src.storage.markdown import MarkdownStorage


class GoogleCalendarAuth:
    """Handle Google Calendar OAuth authentication."""

    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self._service = None

    def get_service(self):
        """Get or create authenticated Google Calendar service."""
        if self._service is not None:
            return self._service

        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            if not self.token_file.exists():
                raise FileNotFoundError(
                    "No token file. Run 'fireschedule gcal-auth' to authenticate."
                )

            credentials = Credentials.from_authorized_user_info(
                json.loads(self.token_file.read_text()),
                self.SCOPES
            )

            self._service = build("calendar", "v3", credentials=credentials)
            return self._service
        except ImportError:
            raise ImportError(
                "google-auth and google-api-python-client are required. "
                "Install with: pip install google-auth google-api-python-client"
            )

    def authenticate(self, credentials_path: str) -> bool:
        """Perform OAuth flow and save token."""
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, self.SCOPES
            )
            
            credentials = flow.run_local_server(port=0)
            
            token_data = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            }
            
            self.token_file.write_text(json.dumps(token_data, indent=2))
            self._service = build("calendar", "v3", credentials=credentials)
            return True
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False

    def is_authenticated(self) -> bool:
        """Check if already authenticated."""
        return self.token_file.exists()


class GoogleCalendarClient:
    """Google Calendar API client for pull/push operations."""

    def __init__(self, auth: GoogleCalendarAuth, calendar_id: str = "primary"):
        self.auth = auth
        self.calendar_id = calendar_id

    def pull_events(self, days_ahead: int = 7) -> list[BaseEvent]:
        """Pull events from Google Calendar."""
        service = self.auth.get_service()
        
        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days_ahead)).isoformat() + "Z"

        events_result = service.events().list(
            calendarId=self.calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = []
        for gcal_event in events_result.get("items", []):
            try:
                event = self._convert_from_gcal(gcal_event)
                if event:
                    events.append(event)
            except Exception as e:
                print(f"Warning: Skipping event {gcal_event.get('id')}: {e}")
                continue

        return events

    def push_event(self, event: BaseEvent) -> Optional[str]:
        """Push a FireSchedule event to Google Calendar."""
        service = self.auth.get_service()
        
        gcal_event = self._convert_to_gcal(event)
        
        try:
            created_event = service.events().insert(
                calendarId=self.calendar_id,
                body=gcal_event
            ).execute()
            return created_event.get("id")
        except Exception as e:
            print(f"Error pushing event: {e}")
            return None

    def sync_events(self, storage: MarkdownStorage, days_ahead: int = 7) -> dict:
        """Bi-directional sync: pull from GCal, push local events to GCal."""
        gcal_events = self.pull_events(days_ahead)
        
        imported_count = 0
        for event in gcal_events:
            storage.save_event(event)
            imported_count += 1

        local_events = []
        for cat in Category:
            local_events.extend(storage.list_events(cat))

        exported_count = 0
        for event in local_events:
            if not hasattr(event, 'gcal_id') or not event.gcal_id:
                gcal_id = self.push_event(event)
                if gcal_id:
                    event.gcal_id = gcal_id
                    storage.save_event(event)
                    exported_count += 1

        return {
            "imported": imported_count,
            "exported": exported_count,
            "total_gcal": len(gcal_events),
            "total_local": len(local_events)
        }

    def _convert_from_gcal(self, gcal_event: dict) -> Optional[BaseEvent]:
        """Convert Google Calendar event to BaseEvent."""
        event_id = gcal_event.get("id", "")
        summary = gcal_event.get("summary", "Untitled")
        description = gcal_event.get("description", "")
        
        start = gcal_event.get("start", {})
        end = gcal_event.get("end", {})
        
        date_str = ""
        time_str = None
        
        if "dateTime" in start:
            dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
            time_str = dt.strftime("%H:%M")
        elif "date" in start:
            date_str = start["date"]
        
        if not date_str:
            return None

        duration = 60
        if "dateTime" in start and "dateTime" in end:
            start_dt = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end["dateTime"].replace("Z", "+00:00"))
            duration = int((end_dt - start_dt).total_seconds() / 60)

        event = BaseEvent(
            id=f"gcal-{event_id[:20]}",
            title=summary,
            category=Category.SOCIAL,
            event_type=EventType.SESSION,
            date=date_str,
            time=time_str,
            duration_minutes=duration,
            priority=Priority.MEDIUM,
            description=description,
            completed=False,
        )
        event.gcal_id = event_id
        return event

    def _convert_to_gcal(self, event: BaseEvent) -> dict:
        """Convert BaseEvent to Google Calendar event format."""
        start_datetime = f"{event.date}T{event.time or '09:00'}:00"
        
        hours = event.duration_minutes // 60
        minutes = event.duration_minutes % 60
        end_datetime = f"{event.date}T{event.time or '09:00'}:00"
        
        if event.time:
            hour, minute = map(int, event.time.split(":"))
            end_hour = hour + hours
            end_minute = minute + minutes
            if end_minute >= 60:
                end_hour += end_minute // 60
                end_minute = end_minute % 60
            end_datetime = f"{event.date}T{end_hour:02d}:{end_minute:02d}:00"
        else:
            end_datetime = f"{event.date}T{9 + hours:02d}:{minutes:02d}:00"

        gcal_event = {
            "summary": event.title,
            "description": event.description or "",
            "start": {"dateTime": start_datetime},
            "end": {"dateTime": end_datetime},
        }

        return gcal_event


class SyncStatus:
    """Track and manage sync status."""

    def __init__(self, status_file: Path = Path(".gcal_sync_status")):
        self.status_file = status_file
        self._status = self._load()

    def _load(self) -> dict:
        if self.status_file.exists():
            return json.loads(self.status_file.read_text())
        return {
            "last_sync": None,
            "last_import": 0,
            "last_export": 0,
            "status": "never_synced"
        }

    def save(self):
        self.status_file.write_text(json.dumps(self._status, indent=2))

    def update(self, imported: int = 0, exported: int = 0, status: str = "synced"):
        self._status = {
            "last_sync": datetime.now().isoformat(),
            "last_import": imported,
            "last_export": exported,
            "status": status
        }
        self.save()

    @property
    def last_sync(self) -> Optional[str]:
        return self._status.get("last_sync")

    @property
    def status(self) -> str:
        return self._status.get("status", "never_synced")
