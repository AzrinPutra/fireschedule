"""FireSchedule TUI Screens."""

from datetime import datetime, timedelta

from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Container, VerticalScroll

from src.tui.widgets import WeekView


class MenuScreen(Screen):
    """Main menu screen."""

    def __init__(self, name: str = None):
        super().__init__(name=name)

    def compose(self):
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
        self.app.bind("d", "push_screen('dashboard')", "Dashboard")

    def on_screen_resumed(self) -> None:
        self.query_one("#title", Static).focus()


class DashboardScreen(Screen):
    """Week view dashboard screen."""

    def __init__(self, name: str = None):
        super().__init__(name=name)
        self.week_view: WeekView = None

    def compose(self):
        from src.integrations.gcal import GoogleCalendarAuth, SyncStatus
        from src.config import config
        
        config.load()
        gcal_config = config.data.get("gcal", {})
        
        auth = GoogleCalendarAuth(
            credentials_file=gcal_config.get("credentials_file", "credentials.json"),
            token_file=gcal_config.get("token_file", "token.json")
        )
        
        sync_status = "🔴 Not connected"
        if auth.is_authenticated():
            status = SyncStatus()
            if status.last_sync:
                sync_status = f"🟢 Synced: {status.last_sync[:16]}"
            else:
                sync_status = "🟡 Authenticated"
        
        yield Container(
            Static("📅 Week Dashboard", id="dashboard-title"),
            Static(sync_status, id="sync-status"),
            VerticalScroll(WeekView(id="week-view")),
            Static("\n[j/k] Navigate  [h/l] Prev/Next Week  [q] Quit", id="nav-hint"),
            id="dashboard",
        )

    def on_mount(self) -> None:
        self.week_view = self.query_one("#week-view", WeekView)
        self._setup_keybindings()

    def _setup_keybindings(self):
        self.app.bind("j", self._navigate_down, "Down")
        self.app.bind("k", self._navigate_up, "Up")
        self.app.bind("h", self._prev_week, "Prev Week")
        self.app.bind("l", self._next_week, "Next Week")

    def action_navigate_down(self):
        if self.week_view:
            self.week_view.navigate_down()

    def action_navigate_up(self):
        if self.week_view:
            self.week_view.navigate_up()

    def action_prev_week(self):
        if self.week_view:
            self.week_view.prev_week()

    def action_next_week(self):
        if self.week_view:
            self.week_view.next_week()

    def _navigate_down(self):
        self.action_navigate_down()

    def _navigate_up(self):
        self.action_navigate_up()

    def _prev_week(self):
        self.action_prev_week()

    def _next_week(self):
        self.action_next_week()
