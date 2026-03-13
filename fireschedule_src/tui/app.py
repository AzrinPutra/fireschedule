"""FireSchedule TUI Application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static

from fireschedule_src.tui.screens import MenuScreen, DashboardScreen, AddEventScreen, ListEventsScreen, BackupScreen, SettingsScreen
from fireschedule_src.tui.theme import FIRESCHEDULE_THEME


class FireScheduleApp(App):
    """Main FireSchedule TUI Application."""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("m", "push_screen('menu')", "Menu"),
        Binding("d", "push_screen('dashboard')", "Dashboard"),
        Binding("escape", "pop_screen", "Back", show=False),
    ]

    SCREENS = {
        "menu": MenuScreen,
        "dashboard": DashboardScreen,
        "add_event": AddEventScreen,
        "list_events": ListEventsScreen,
        "backup": BackupScreen,
        "settings": SettingsScreen,
    }

    CSS = """
Screen {
    background: $surface;
}

#title {
    height: 3;
    content-align: center middle;
    text-style: bold;
    color: $primary;
}

#menu-options {
    height: auto;
    margin: 1 2;
}

.menu-item {
    padding: 1 2;
    dock: top;
}

.menu-item:hover {
    background: $accent;
}

#dashboard {
    padding: 1 2;
}

#week-view {
    height: auto;
}

#sync-status {
    color: $text;
    margin: 1 2;
}

#dashboard-title {
    text-style: bold;
    color: $primary;
}

#form-title, #events-title, #backup-title, #settings-title {
    text-style: bold;
    color: $primary;
    height: 3;
    content-align: center middle;
}

#form-container, #events-container, #backup-container, #settings-container {
    margin: 1 2;
}

Input, Select, TextArea {
    margin: 0 1;
}

#form-buttons, #backup-buttons {
    height: auto;
    align: center middle;
    margin: 1 2;
}

Button {
    margin: 0 1;
}

#form-hint, #filter-hint, #backup-hint, #settings-hint {
    color: $text-muted;
    margin: 1 2;
}
"""

    CSS_VARIABLES = {
        "primary": FIRESCHEDULE_THEME["primary"],
        "secondary": FIRESCHEDULE_THEME["secondary"],
        "accent": FIRESCHEDULE_THEME["accent"],
        "surface": FIRESCHEDULE_THEME["surface"],
        "background": FIRESCHEDULE_THEME["background"],
        "text": FIRESCHEDULE_THEME["text"],
        "success": FIRESCHEDULE_THEME["success"],
        "warning": FIRESCHEDULE_THEME["warning"],
        "error": FIRESCHEDULE_THEME["error"],
    }

    def __init__(self):
        super().__init__()

    def on_mount(self) -> None:
        """Handle app mount."""
        self.push_screen("menu")

    def compose(self) -> ComposeResult:
        """Compose the app screens."""
        yield Header()
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    def action_goto_dashboard(self) -> None:
        """Go to dashboard."""
        self.push_screen("dashboard")
