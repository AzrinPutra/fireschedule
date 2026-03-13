"""FireSchedule TUI Screens."""

from textual.screen import Screen
from textual.widgets import Static, Button
from textual.containers import Container, VerticalScroll


class MenuScreen(Screen):
    """Main menu screen."""

    def __init__(self, name: str = None):
        super().__init__(name=name)

    def compose(self):
        """Compose the menu screen."""
        yield Container(
            Static("🔥 FireSchedule", id="title"),
            VerticalScroll(
                Static("1. View Dashboard (Week Overview)", id="menu-option-1"),
                Static("2. Add Event", id="menu-option-2"),
                Static("3. List Events", id="menu-option-3"),
                Static("4. Git Backup", id="menu-option-4"),
                Static("5. Settings", id="menu-option-5"),
                id="menu-options",
            ),
            Static("\n[Press D for Dashboard, Q to quit]", id="footer-hint"),
        )

    def on_mount(self) -> None:
        """Set up key listeners."""
        self.app.bind("d", "push_screen('dashboard')", "Dashboard")

    def on_screen_resumed(self) -> None:
        """Called when screen is resumed."""
        self.query_one("#title", Static).focus()


class DashboardScreen(Screen):
    """Week view dashboard screen."""

    def __init__(self, name: str = None):
        super().__init__(name=name)

    def compose(self):
        """Compose the dashboard screen."""
        yield Container(
            Static("📅 Week Dashboard", id="dashboard-title"),
            VerticalScroll(id="week-view"),
            id="dashboard",
        )

    def on_mount(self) -> None:
        """Populate week view on mount."""
        week_view = self.query_one("#week-view", VerticalScroll)
        week_view.mount(Static(self._generate_week_view()))

    def _generate_week_view(self) -> str:
        """Generate the week view content."""
        from datetime import datetime, timedelta

        today = datetime.now()
        days = []
        for i in range(7):
            day = today + timedelta(days=i)
            day_name = day.strftime("%A")
            day_date = day.strftime("%b %d")
            days.append(f"{day_name:10} | {day_date} | (no events)")

        header = "Day         | Date      | Events\n" + "-" * 40
        return header + "\n" + "\n".join(days)
