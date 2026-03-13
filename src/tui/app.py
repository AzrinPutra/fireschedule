"""FireSchedule TUI Application."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Static

from src.tui.screens import MenuScreen, DashboardScreen
from src.tui.theme import FIRESCHEDULE_THEME


class FireScheduleApp(App):
    """Main FireSchedule TUI Application."""

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("m", "push_screen('menu')", "Menu"),
        Binding("d", "push_screen('dashboard')", "Dashboard"),
        Binding("escape", "pop_screen", "Back", show=False),
    ]

    CSS = """
    Screen {
        background: $surface;
    }
    
    # title {
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $primary;
    }
    
    # menu-options {
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
    
    # dashboard {
        padding: 1 2;
    }
    
    # week-view {
        height: auto;
    }
    """

    def __init__(self):
        super().__init__()
        self.theme = FIRESCHEDULE_THEME

    def on_mount(self) -> None:
        """Handle app mount."""
        self.push_screen("menu")

    def compose(self) -> ComposeResult:
        """Compose the app screens."""
        yield Header()
        yield MenuScreen("menu", name="menu")
        yield DashboardScreen("dashboard", name="dashboard")
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
