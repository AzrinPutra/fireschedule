"""FireSchedule TUI Application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static

from fireschedule_src.tui.screens import MenuScreen, DashboardScreen
from fireschedule_src.tui.theme import FIRESCHEDULE_THEME


class FireScheduleApp(App):
    """Main FireSchedule TUI Application."""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("m", "push_screen('menu')", "Menu"),
        Binding("d", "push_screen('dashboard')", "Dashboard"),
        Binding("escape", "pop_screen", "Back", show=False),
        Binding("1", "goto_dashboard", "Dashboard", show=False),
        Binding("2", "cli_add", "Add", show=False),
        Binding("3", "cli_list", "List", show=False),
        Binding("4", "cli_backup", "Backup", show=False),
        Binding("5", "cli_settings", "Settings", show=False),
    ]

    SCREENS = {
        "menu": MenuScreen,
        "dashboard": DashboardScreen,
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

    def action_cli_add(self) -> None:
        """Add new event via CLI."""
        import sys
        self.exit()
        sys.argv = ["fireschedule", "add", "--help"]

    def action_cli_list(self) -> None:
        """List events via CLI."""
        import sys
        self.exit()
        sys.argv = ["fireschedule", "list-events"]

    def action_cli_backup(self) -> None:
        """Show backup instructions."""
        self.exit()
        print("\nTo backup your data, run: ./scripts/backup.sh")

    def action_cli_settings(self) -> None:
        """Show settings instructions."""
        self.exit()
        print("\nTo edit settings, edit config.yaml")
