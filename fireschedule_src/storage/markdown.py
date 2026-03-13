from datetime import datetime
from pathlib import Path
from typing import Any

from ..models.events import (
    BaseEvent,
    Category,
    EventType,
    Priority,
    SchoolEvent,
    LearningEvent,
    ExerciseEvent,
    SocialEvent,
)
class MarkdownStorage:
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        for category in Category:
            (self.base_path / category.value).mkdir(parents=True, exist_ok=True)

    def _get_category_path(self, category) -> Path:
        cat_value = category.value if hasattr(category, 'value') else category
        return self.base_path / cat_value

    def _event_to_markdown(self, event: BaseEvent) -> str:
        lines = [
            f"# {event.title}",
            f"",
            f"**ID:** {event.id}",
            f"**Category:** {event.category}",
            f"**Type:** {event.event_type}",
            f"**Date:** {event.date}",
        ]
        
        if event.time:
            lines.append(f"**Time:** {event.time}")
        
        if hasattr(event, 'language') and event.language:
            lines.append(f"**Language:** {event.language}")
        
        if hasattr(event, 'topic') and event.topic:
            lines.append(f"**Topic:** {event.topic}")
        
        lines.extend([
            f"**Duration:** {event.duration_minutes} minutes",
            f"**Priority:** {event.priority}",
            f"**Completed:** {'Yes' if event.completed else 'No'}",
        ])
        
        if event.description:
            lines.extend(["", f"## Description", "", event.description])
        
        lines.extend([
            "",
            f"*Created: {event.created_at.isoformat()}*",
            f"*Updated: {event.updated_at.isoformat()}*",
        ])
        
        return "\n".join(lines)

    def _markdown_to_event(self, category: Category, content: str) -> dict[str, Any]:
        lines = content.split("\n")
        event_data: dict[str, Any] = {
            "category": category.value if hasattr(category, 'value') else category,
            "event_type": "session",
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith("# "):
                event_data["title"] = line[2:].strip()
            elif line.startswith("**ID:**"):
                event_data["id"] = line.replace("**ID:**", "", 1).strip()
            elif line.startswith("**Date:**"):
                event_data["date"] = line.replace("**Date:**", "", 1).strip()
            elif line.startswith("**Time:**"):
                event_data["time"] = line.replace("**Time:**", "", 1).strip()
            elif line.startswith("**Duration:**"):
                parts = line.replace("**Duration:**", "", 1).strip().split()
                if parts:
                    try:
                        event_data["duration_minutes"] = int(parts[0])
                    except (ValueError, IndexError):
                        pass
            elif line.startswith("**Priority:**"):
                priority = line.replace("**Priority:**", "", 1).strip()
                if "." in priority:
                    priority = priority.split(".")[-1]
                event_data["priority"] = priority.lower()
            elif line.startswith("**Completed:**"):
                event_data["completed"] = "Yes" in line
            elif line.startswith("**Language:**"):
                event_data["language"] = line.replace("**Language:**", "", 1).strip()
            elif line.startswith("**Topic:**"):
                event_data["topic"] = line.replace("**Topic:**", "", 1).strip()
            elif line.startswith("**Type:**"):
                event_data["event_type"] = line.replace("**Type:**", "", 1).strip()
        
        return event_data

    def save_event(self, event: BaseEvent) -> None:
        category_path = self._get_category_path(event.category)
        filename = f"{event.date}_{event.id}.md"
        filepath = category_path / filename
        
        with open(filepath, "w") as f:
            f.write(self._event_to_markdown(event))

    def load_event(self, category: Category, event_id: str, date: str) -> BaseEvent | None:
        category_path = self._get_category_path(category)
        filename = f"{date}_{event_id}.md"
        filepath = category_path / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, "r") as f:
            content = f.read()
        
        event_data = self._markdown_to_event(category, content)
        
        event_classes = {
            Category.SCHOOL: SchoolEvent,
            Category.LEARNING: LearningEvent,
            Category.EXERCISE: ExerciseEvent,
            Category.SOCIAL: SocialEvent,
        }
        
        event_class = event_classes.get(category, BaseEvent)
        return event_class(**event_data)

    def list_events(self, category: Category, date: str | None = None) -> list[BaseEvent]:
        category_path = self._get_category_path(category)
        events = []
        
        pattern = f"{date}_*.md" if date else "*.md"
        
        for filepath in category_path.glob(pattern):
            with open(filepath, "r") as f:
                content = f.read()
            
            event_data = self._markdown_to_event(category, content)
            event_classes = {
                Category.SCHOOL: SchoolEvent,
                Category.LEARNING: LearningEvent,
                Category.EXERCISE: ExerciseEvent,
                Category.SOCIAL: SocialEvent,
            }
            event_class = event_classes.get(category, BaseEvent)
            
            try:
                event = event_class(**event_data)
                events.append(event)
            except Exception:
                continue
        
        return events

    def delete_event(self, category: Category, event_id: str, date: str) -> bool:
        category_path = self._get_category_path(category)
        filename = f"{date}_{event_id}.md"
        filepath = category_path / filename
        
        if filepath.exists():
            filepath.unlink()
            return True
        return False


storage = MarkdownStorage()
