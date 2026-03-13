"""Notion Integration Module.

Provides export/import functionality for Notion-compatible formats.
"""

import json
import csv
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.models.events import (
    BaseEvent, Category, EventType, Priority,
    SchoolEvent, LearningEvent, ExerciseEvent, SocialEvent
)
from src.storage.markdown import MarkdownStorage


class NotionExporter:
    """Export FireSchedule events to Notion-compatible formats."""

    def __init__(self, storage: MarkdownStorage):
        self.storage = storage

    def export_to_markdown(self, output_path: Path) -> int:
        """Export all events to a Markdown file compatible with Notion import.
        
        Returns the number of events exported.
        """
        events = self._load_all_events()
        
        if not events:
            return 0

        lines = []
        lines.append("# FireSchedule Export")
        lines.append(f"\n*Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")

        by_category = {}
        for event in events:
            cat = event.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(event)

        for cat_name, cat_events in sorted(by_category.items()):
            lines.append(f"## {cat_name.title()}")
            lines.append("")
            
            for event in sorted(cat_events, key=lambda e: e.date):
                lines.append(f"### {event.title}")
                lines.append(f"**Date:** {event.date}")
                if event.time:
                    lines.append(f"**Time:** {event.time}")
                lines.append(f"**Duration:** {event.duration_minutes} minutes")
                lines.append(f"**Type:** {event.event_type.value}")
                lines.append(f"**Priority:** {event.priority.value}")
                
                if event.description:
                    lines.append(f"\n{event.description}")
                
                if isinstance(event, LearningEvent) and event.language:
                    lines.append(f"\n**Language:** {event.language}")
                    if event.topic:
                        lines.append(f"**Topic:** {event.topic}")
                    if event.notes:
                        lines.append(f"\n**Notes:** {event.notes}")
                
                if isinstance(event, ExerciseEvent) and event.exercise_type:
                    lines.append(f"\n**Exercise:** {event.exercise_type}")
                    if event.location:
                        lines.append(f"**Location:** {event.location}")
                
                if isinstance(event, SocialEvent) and event.people:
                    lines.append(f"\n**People:** {', '.join(event.people)}")
                    if event.location:
                        lines.append(f"**Location:** {event.location}")
                
                lines.append("")
                lines.append("---")
                lines.append("")

        output_path.write_text("\n".join(lines))
        return len(events)

    def export_to_csv(self, output_path: Path) -> int:
        """Export all events to a CSV file.
        
        Returns the number of events exported.
        """
        events = self._load_all_events()
        
        if not events:
            return 0

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'id', 'title', 'category', 'event_type', 'date', 'time',
                'duration_minutes', 'priority', 'description', 'completed',
                'language', 'topic', 'exercise_type', 'people', 'location'
            ])
            
            for event in events:
                writer.writerow([
                    event.id,
                    event.title,
                    event.category.value,
                    event.event_type.value,
                    event.date,
                    event.time or '',
                    event.duration_minutes,
                    event.priority.value,
                    event.description or '',
                    event.completed,
                    getattr(event, 'language', '') or '',
                    getattr(event, 'topic', '') or '',
                    getattr(event, 'exercise_type', '') or '',
                    ','.join(getattr(event, 'people', [])) or '',
                    getattr(event, 'location', '') or '',
                ])

        return len(events)

    def _load_all_events(self) -> list[BaseEvent]:
        """Load all events from storage."""
        events = []
        for cat in Category:
            events.extend(self.storage.list_events(cat))
        return events


class NotionImporter:
    """Import events from Notion exports."""

    def __init__(self, storage: MarkdownStorage):
        self.storage = storage

    def import_from_csv(self, csv_path: Path) -> int:
        """Import events from a CSV file.
        
        Returns the number of events imported.
        """
        count = 0
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    category = Category(row['category'])
                    event_type = EventType(row['event_type'])
                    
                    if category == Category.LEARNING:
                        event = LearningEvent(
                            id=row['id'],
                            title=row['title'],
                            category=category,
                            event_type=event_type,
                            date=row['date'],
                            time=row['time'] or None,
                            duration_minutes=int(row['duration_minutes']),
                            priority=Priority(row['priority']),
                            description=row['description'] or None,
                            completed=bool(row['completed']),
                            language=row['language'],
                            topic=row['topic'] or None,
                        )
                    elif category == Category.EXERCISE:
                        event = ExerciseEvent(
                            id=row['id'],
                            title=row['title'],
                            category=category,
                            event_type=event_type,
                            date=row['date'],
                            time=row['time'] or None,
                            duration_minutes=int(row['duration_minutes']),
                            priority=Priority(row['priority']),
                            description=row['description'] or None,
                            completed=bool(row['completed']),
                            exercise_type=row['exercise_type'],
                            location=row['location'] or None,
                        )
                    elif category == Category.SOCIAL:
                        event = SocialEvent(
                            id=row['id'],
                            title=row['title'],
                            category=category,
                            event_type=event_type,
                            date=row['date'],
                            time=row['time'] or None,
                            duration_minutes=int(row['duration_minutes']),
                            priority=Priority(row['priority']),
                            description=row['description'] or None,
                            completed=bool(row['completed']),
                            people=row['people'].split(',') if row['people'] else [],
                            location=row['location'] or None,
                        )
                    else:
                        event = BaseEvent(
                            id=row['id'],
                            title=row['title'],
                            category=category,
                            event_type=event_type,
                            date=row['date'],
                            time=row['time'] or None,
                            duration_minutes=int(row['duration_minutes']),
                            priority=Priority(row['priority']),
                            description=row['description'] or None,
                            completed=bool(row['completed']),
                        )
                    
                    self.storage.save_event(event)
                    count += 1
                except Exception as e:
                    print(f"Warning: Skipping row due to error: {e}")
                    continue

        return count


class NotionClient:
    """Direct Notion API client (optional, requires API token)."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

    def create_page(self, database_id: str, title: str, content: str = "") -> Optional[dict]:
        """Create a new page in a Notion database."""
        import requests
        
        url = f"{self.base_url}/pages"
        
        properties = {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        }
        
        if content:
            properties["content"] = {
                "rich_text": [{"text": {"content": content}}]
            }
        
        data = {
            "parent": {"database_id": database_id},
            "properties": properties
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating Notion page: {e}")
            return None
