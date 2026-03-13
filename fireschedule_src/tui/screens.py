"""FireSchedule TUI Screens."""

from datetime import datetime, timedelta
import subprocess
import os

from textual.screen import Screen
from textual.widgets import Static, Input, Button, Select, TextArea
from textual.containers import Container, VerticalScroll, Horizontal
from textual import work

from fireschedule_src.tui.widgets import WeekView


class MenuScreen(Screen):
    """Main menu screen."""

    def __init__(self, name: str = "menu"):
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
            Static("\n[1-5] Select  [D] Dashboard  [Q] Quit", id="footer-hint"),
        )

    def on_mount(self) -> None:
        self.app.bind("escape", "quit_app")
        self.app.bind("d", "push_screen('dashboard')")
        self.app.bind("1", "push_screen('dashboard')")
        self.app.bind("2", "push_screen('add_event')")
        self.app.bind("3", "push_screen('list_events')")
        self.app.bind("4", "push_screen('backup')")
        self.app.bind("5", "push_screen('settings')")

    def action_quit_app(self):
        self.app.exit()


class AddEventScreen(Screen):
    """Add event screen with form."""

    def __init__(self, name: str = "add_event"):
        super().__init__(name=name)
        self.form_data = {}

    def compose(self):
        yield Container(
            Static("➕ Add New Event", id="form-title"),
            VerticalScroll(
                Static("Title:", id="label-title"),
                Input(placeholder="Enter event title...", id="input-title"),
                Static("\nCategory:", id="label-category"),
                Select(
                    [
                        ("school", "School"),
                        ("learning", "Learning"),
                        ("exercise", "Exercise"),
                        ("social", "Social"),
                    ],
                    id="input-category",
                ),
                Static("\nDate (YYYY-MM-DD):", id="label-date"),
                Input(value=datetime.now().strftime("%Y-%m-%d"), id="input-date"),
                Static("\nTime (HH:MM):", id="label-time"),
                Input(value="09:00", placeholder="e.g., 14:00", id="input-time"),
                Static("\nDuration (minutes):", id="label-duration"),
                Input(value="60", id="input-duration"),
                Static("\nDescription:", id="label-desc"),
                TextArea(placeholder="Optional description...", id="input-desc"),
                id="form-container",
            ),
            Horizontal(
                Button("Add Event", variant="primary", id="btn-submit"),
                Button("Cancel", variant="default", id="btn-cancel"),
                id="form-buttons",
            ),
            Static("\n[ESC] Back to Menu", id="form-hint"),
        )

    def on_mount(self) -> None:
        self.app.bind("escape", "pop_screen")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-submit":
            self.submit_event()

    def submit_event(self):
        from fireschedule_src.models.events import Category, EventType, BaseEvent, Priority
        from fireschedule_src.storage.markdown import MarkdownStorage

        title = self.query_one("#input-title", Input).value
        category = self.query_one("#input-category", Select).value
        date = self.query_one("#input-date", Input).value
        time = self.query_one("#input-time", Input).value
        duration = self.query_one("#input-duration", Input).value
        description = self.query_one("#input-desc", TextArea).text

        if not title:
            self.query_one("#input-title", Input).focus()
            return
        if not category or category == Select.NO_SELECTION:
            self.query_one("#input-category", Select).focus()
            return

        try:
            event = BaseEvent(
                id=f"event-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                title=title,
                category=Category[category.upper()],
                event_type=EventType.SESSION,
                date=date or datetime.now().strftime("%Y-%m-%d"),
                time=time or "09:00",
                duration_minutes=int(duration) if duration else 60,
                description=description,
                priority=Priority.MEDIUM,
            )

            storage = MarkdownStorage()
            storage.save_event(event)

            self.query_one("#form-title", Static).update("✅ Event Added Successfully!")
            self.app.pop_screen()
        except Exception as e:
            self.query_one("#form-title", Static).update(f"❌ Error: {str(e)}")


class ListEventsScreen(Screen):
    """List events screen."""

    def __init__(self, name: str = "list_events"):
        super().__init__(name=name)

    def compose(self):
        yield Container(
            Static("📋 Events List", id="events-title"),
            VerticalScroll(
                Static("Loading events...", id="events-list"),
                id="events-container",
            ),
            Static("\n[1] Today  [2] Week  [3] All  [ESC] Back", id="filter-hint"),
        )

    def on_mount(self) -> None:
        self.app.bind("escape", "pop_screen")
        self.app.bind("1", "filter_today")
        self.app.bind("2", "filter_week")
        self.app.bind("3", "filter_all")
        self.load_events("all")

    def load_events(self, filter_type: str):
        from fireschedule_src.models.events import Category
        from fireschedule_src.storage.markdown import MarkdownStorage

        storage = MarkdownStorage()
        events = []
        for cat in Category:
            events.extend(storage.list_events(cat))

        today_str = datetime.now().strftime("%Y-%m-%d")
        today_date = datetime.now().date()
        week_end = today_date + timedelta(days=7)

        if filter_type == "today":
            events = [e for e in events if e.date == today_str]
        elif filter_type == "week":
            events = [e for e in events if today_date <= datetime.strptime(e.date, "%Y-%m-%d").date() < week_end]

        events.sort(key=lambda e: (e.date, e.time or "00:00"))

        if not events:
            content = "No events found."
        else:
            lines = []
            for event in events:
                cat = str(event.category).split('.')[-1].lower()
                lines.append(f"▸ {event.date} {event.time or '':5} [{cat:8}] {event.title}")
            content = "\n".join(lines)

        self.query_one("#events-list", Static).update(content)
        self.query_one("#events-title", Static).update(f"📋 Events ({len(events)} found)")

    def action_filter_today(self):
        self.load_events("today")

    def action_filter_week(self):
        self.load_events("week")

    def action_filter_all(self):
        self.load_events("all")


class BackupScreen(Screen):
    """Git backup screen."""

    def __init__(self, name: str = "backup"):
        super().__init__(name=name)

    def compose(self):
        yield Container(
            Static("🔄 Git Backup", id="backup-title"),
            VerticalScroll(
                Static("Click 'Run Backup' to backup your data to GitHub.", id="backup-info"),
                Static("", id="backup-output"),
                id="backup-container",
            ),
            Horizontal(
                Button("Run Backup", variant="primary", id="btn-backup"),
                Button("Cancel", variant="default", id="btn-cancel"),
                id="backup-buttons",
            ),
            Static("\n[ESC] Back to Menu", id="backup-hint"),
        )

    def on_mount(self) -> None:
        self.app.bind("escape", "pop_screen")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.app.pop_screen()
        elif event.button.id == "btn-backup":
            self.run_backup()

    @work(exclusive=True, thread=True)
    def run_backup(self):
        output = self.query_one("#backup-output", Static)
        output.update("Running backup...\n")

        try:
            result = subprocess.run(
                ["./scripts/backup.sh"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                output.update(f"✅ Backup completed successfully!\n\n{result.stdout}")
            else:
                output.update(f"❌ Backup failed:\n{result.stderr}")
        except subprocess.TimeoutExpired:
            output.update("❌ Backup timed out")
        except FileNotFoundError:
            output.update("❌ Backup script not found at ./scripts/backup.sh")
        except Exception as e:
            output.update(f"❌ Error: {str(e)}")


class SettingsScreen(Screen):
    """Settings screen."""

    def __init__(self, name: str = "settings"):
        super().__init__(name=name)

    def compose(self):
        from fireschedule_src.config import config

        config.load()
        gcal = config.get("gcal", {})
        notion = config.get("notion", {})

        yield Container(
            Static("⚙️ Settings", id="settings-title"),
            VerticalScroll(
                Static("Google Calendar:", id="gcal-header"),
                Static(
                    f"  Connected: {'Yes' if gcal.get('connected') else 'No'}\n"
                    f"  Credentials: {gcal.get('credentials_file', 'Not set')}\n"
                    f"  Token: {gcal.get('token_file', 'Not set')}",
                    id="gcal-info",
                ),
                Static("\nNotion:", id="notion-header"),
                Static(
                    f"  Export: {notion.get('export_enabled', False)}\n"
                    f"  Import: {notion.get('import_enabled', False)}",
                    id="notion-info",
                ),
                Static("\nReminders:", id="reminders-header"),
                Static(
                    f"  Enabled: {config.get('reminders', {}).get('enabled', False)}\n"
                    f"  Minutes before: {config.get('reminders', {}).get('default_minutes_before', 15)}",
                    id="reminders-info",
                ),
                id="settings-container",
            ),
            Static("\n[ESC] Back to Menu  [E] Edit config.yaml", id="settings-hint"),
        )

    def on_mount(self) -> None:
        self.app.bind("escape", "pop_screen")


class DashboardScreen(Screen):
    """Week view dashboard screen."""

    def __init__(self, name: str = None):
        super().__init__(name=name)
        self.week_view: WeekView = None

    def compose(self):
        from fireschedule_src.integrations.gcal import GoogleCalendarAuth, SyncStatus
        from fireschedule_src.config import config
        
        config.load()
        gcal_config = config.get("gcal", {})
        
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
            Static("\n[j/k] Navigate  [h/l] Prev/Next Week  [ESC] Back to Menu  [Q] Quit", id="nav-hint"),
            id="dashboard",
        )

    def on_mount(self) -> None:
        self.week_view = self.query_one("#week-view", WeekView)
        self._setup_keybindings()

    def _setup_keybindings(self):
        self.app.bind("j", "navigate_down")
        self.app.bind("k", "navigate_up")
        self.app.bind("h", "prev_week")
        self.app.bind("l", "next_week")
        self.app.bind("escape", "go_back")

    def action_go_back(self):
        self.app.pop_screen()

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
