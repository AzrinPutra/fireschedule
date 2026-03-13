"""FireSchedule TUI Widgets."""

from datetime import datetime, timedelta
from typing import Optional, List

from textual.widget import Widget
from textual.widgets import Static
from textual.message import Message

from src.tui.theme import CATEGORY_COLORS, TIME_SLOTS


class WeekView(Widget):
    """Week view widget with navigation support."""

    class Navigate(Message):
        """Navigation message."""

        def __init__(self, direction: str) -> None:
            super().__init__()
            self.direction = direction

    def __init__(self, start_date: Optional[datetime] = None, **kwargs):
        super().__init__(**kwargs)
        self.start_date = start_date or datetime.now()
        self.selected_day = 0
        self.selected_slot = 0

    def compose(self):
        yield Static("", id="week-content")

    def on_mount(self) -> None:
        self.refresh_week_view()

    def refresh_week_view(self, new_start_date: Optional[datetime] = None):
        if new_start_date:
            self.start_date = new_start_date

        content = self._generate_week_view()
        self.query_one("#week-content", Static).update(content)

    def _generate_week_view(self) -> str:
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════╗")
        lines.append("║                    📅 WEEK VIEW                                 ║")
        lines.append("╠══════════════════════════════════════════════════════════════════╣")

        for day_offset in range(7):
            day = self.start_date + timedelta(days=day_offset)
            is_today = day.date() == datetime.now().date()
            day_str = day.strftime("%a %b %d")
            
            if is_today:
                day_str = f"▶ {day_str} ◀"
            
            lines.append(f"║ {day_str:20} │                                          ║")
            
            for slot_idx, slot in enumerate(TIME_SLOTS):
                marker = "→" if day_offset == self.selected_day and slot_idx == self.selected_slot else " "
                lines.append(f"║   {marker} {slot:11} │                                          ║")
            
            lines.append("║                  │                                          ║")

        lines.append("╠══════════════════════════════════════════════════════════════════╣")
        lines.append("║ Navigation: [j/k] up/down  [h/l] prev/next week  [q] back     ║")
        lines.append("╚══════════════════════════════════════════════════════════════════╝")
        
        return "\n".join(lines)

    def navigate_up(self):
        if self.selected_slot > 0:
            self.selected_slot -= 1
        elif self.selected_day > 0:
            self.selected_day -= 1
            self.selected_slot = len(TIME_SLOTS) - 1
        self.refresh_week_view()

    def navigate_down(self):
        if self.selected_slot < len(TIME_SLOTS) - 1:
            self.selected_slot += 1
        elif self.selected_day < 6:
            self.selected_day += 1
            self.selected_slot = 0
        self.refresh_week_view()

    def prev_week(self):
        self.start_date -= timedelta(days=7)
        self.refresh_week_view()

    def next_week(self):
        self.start_date += timedelta(days=7)
        self.refresh_week_view()


class EventCard(Widget):
    """Event card widget for displaying individual events."""

    def __init__(self, event, **kwargs):
        super().__init__(**kwargs)
        self.event = event

    def compose(self):
        color = CATEGORY_COLORS.get(str(self.event.category).split('.')[-1].lower(), "#ffffff")
        title = self.event.title
        time = getattr(self.event, 'time', '')
        
        yield Static(f"[{color}]{title}[/{color}] {time}", id="event-title")
