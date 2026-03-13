"""FireSchedule CLI Commands."""

import click
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import config
from src.models.events import Category, EventType, BaseEvent
from src.storage.markdown import MarkdownStorage

storage = MarkdownStorage()


@click.group()
def cli():
    """FireSchedule - Personal Scheduling Assistant"""
    config.load()


@cli.command()
@click.argument("title")
@click.option("--category", "-c", type=click.Choice(["school", "learning", "exercise", "social"]), required=True, help="Event category")
@click.option("--date", "-d", default=None, help="Event date (YYYY-MM-DD)")
@click.option("--time", "-t", default=None, help="Event time (HH:MM)")
@click.option("--duration", default=60, type=int, help="Duration in minutes")
@click.option("--description", default="", help="Event description")
def add(title: str, category: str, date: Optional[str], time: Optional[str], duration: int, description: str):
    """Add a new event."""
    from src.models.events import Priority
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    event = BaseEvent(
        id=f"event-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        title=title,
        category=Category[category.upper()],
        event_type=EventType.SESSION,
        date=date,
        time=time or "09:00",
        duration_minutes=duration,
        description=description,
        priority=Priority.MEDIUM,
    )
    
    storage.save_event(event)
    click.echo(f"✓ Event '{title}' added successfully!")
    click.echo(f"  ID: {event.id}")
    click.echo(f"  Category: {category}")
    click.echo(f"  Date: {date}")


@cli.command()
@click.option("--today", is_flag=True, help="Show today's events only")
@click.option("--week", is_flag=True, help="Show this week's events")
@click.option("--category", "-c", type=click.Choice(["school", "learning", "exercise", "social"]), help="Filter by category")
def list_events(today: bool, week: bool, category: Optional[str]):
    """List events."""
    from rich.console import Console
    from rich.table import Table
    
    events = []
    for cat in Category:
        events.extend(storage.list_events(cat))
    
    if today:
        today_str = datetime.now().strftime("%Y-%m-%d")
        events = [e for e in events if e.date == today_str]
    elif week:
        today_date = datetime.now().date()
        week_end = today_date + timedelta(days=7)
        events = [e for e in events if today_date <= datetime.strptime(e.date, "%Y-%m-%d").date() < week_end]
    
    if category:
        cat_enum = Category[category.upper()]
        events = [e for e in events if e.category == cat_enum]
    
    console = Console()
    
    if not events:
        click.echo("No events found.")
        return
    
    table = Table(title="Events")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Category", style="magenta")
    table.add_column("Date", style="yellow")
    table.add_column("Time")
    
    for event in events:
        table.add_row(
            event.id,
            event.title,
            str(event.category.value),
            event.date,
            event.time or "-"
        )
    
    console.print(table)
    click.echo(f"\nTotal: {len(events)} event(s)")


@cli.command()
@click.argument("event_id")
@click.option("--title", "-t", help="New title")
@click.option("--date", "-d", help="New date (YYYY-MM-DD)")
@click.option("--time", help="New time (HH:MM)")
@click.option("--category", "-c", type=click.Choice(["school", "learning", "exercise", "social"]), help="New category")
def edit(event_id: str, title: Optional[str], date: Optional[str], time: Optional[str], category: Optional[str]):
    """Edit an existing event."""
    event = storage.load_event(Category.LEARNING, event_id, datetime.now().strftime("%Y-%m-%d"))
    
    if not event:
        for cat in Category:
            event = storage.load_event(cat, event_id, "")
            if event:
                break
    
    if not event:
        click.echo(f"✗ Event '{event_id}' not found.", err=True)
        sys.exit(1)
    
    if title:
        event.title = title
    if date:
        event.date = date
    if time:
        event.time = time
    if category:
        event.category = Category[category.upper()]
    
    storage.save_event(event)
    click.echo(f"✓ Event '{event_id}' updated successfully!")


@cli.command()
@click.argument("event_id")
def delete(event_id: str):
    """Delete an event."""
    success = False
    for cat in Category:
        success = storage.delete_event(cat, event_id, "")
        if success:
            break
    
    if success:
        click.echo(f"✓ Event '{event_id}' deleted successfully!")
    else:
        click.echo(f"✗ Event '{event_id}' not found.", err=True)
        sys.exit(1)


@cli.command()
def view():
    """Open the TUI dashboard."""
    from src.tui.app import FireScheduleApp
    app = FireScheduleApp()
    app.run()


@cli.command()
def reminders():
    """Check and send reminder notifications now."""
    from src.notifications.config import ReminderConfig
    from src.notifications.scheduler import ReminderScheduler
    
    config.load()
    reminder_config = ReminderConfig.from_dict(config.reminders)
    
    scheduler = ReminderScheduler(reminder_config)
    count = scheduler.check_and_notify()
    
    if count > 0:
        click.echo(f"✓ Sent {count} reminder(s)")
    else:
        click.echo("No reminders to send at this time.")


@cli.command()
def reminder_status():
    """Show reminder configuration status."""
    from src.notifications.config import ReminderConfig
    
    config.load()
    reminder_config = ReminderConfig.from_dict(config.reminders)
    
    click.echo("Reminder Configuration:")
    click.echo(f"  Enabled: {reminder_config.enabled}")
    click.echo(f"  Minutes before: {reminder_config.default_minutes_before}")
    click.echo(f"  Daily summary: {reminder_config.daily_summary_enabled}")
    if reminder_config.daily_summary_enabled:
        click.echo(f"  Summary time: {reminder_config.daily_summary_time}")
    click.echo(f"  Sound: {reminder_config.notification_sound}")


@cli.command()
@click.argument("title")
@click.option("--language", "-l", type=click.Choice(["Python", "Bash"]), required=True, help="Programming language")
@click.option("--topic", "-t", default=None, help="Topic being learned")
@click.option("--date", "-d", default=None, help="Event date (YYYY-MM-DD)")
@click.option("--time", default=None, help="Event time (HH:MM)")
@click.option("--duration", default=60, type=int, help="Duration in minutes")
@click.option("--notes", default="", help="Learning notes")
def learn(title: str, language: str, topic: Optional[str], date: Optional[str], time: Optional[str], duration: int, notes: str):
    """Add a learning practice session (Python/Bash)."""
    from src.models.events import LearningEvent, Priority
    
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    event = LearningEvent(
        id=f"learn-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        title=title,
        category=Category.LEARNING,
        event_type=EventType.PRACTICE,
        date=date,
        time=time or "14:00",
        duration_minutes=duration,
        language=language,
        topic=topic,
        notes=notes,
        priority=Priority.MEDIUM,
    )
    
    storage.save_event(event)
    click.echo(f"✓ Learning session '{title}' added!")
    click.echo(f"  Language: {language}")
    click.echo(f"  Topic: {topic or 'General'}")
    click.echo(f"  Date: {date}")


@cli.command()
@click.option("--language", "-l", type=click.Choice(["Python", "Bash", "all"]), default="all", help="Filter by language")
def progress(language: str):
    """Show learning progress statistics."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    events = storage.list_events(Category.LEARNING)
    
    if language != "all":
        events = [e for e in events if hasattr(e, 'language') and e.language == language]
    
    if not events:
        click.echo("No learning sessions found.")
        return
    
    console = Console()
    
    total_sessions = len(events)
    completed_sessions = sum(1 for e in events if e.completed)
    total_minutes = sum(e.duration_minutes for e in events)
    
    languages = {}
    topics = {}
    for e in events:
        if hasattr(e, 'language'):
            lang = e.language
            languages[lang] = languages.get(lang, 0) + 1
        if hasattr(e, 'topic') and e.topic:
            topic = e.topic
            topics[topic] = topics.get(topic, 0) + 1
    
    stats = f"""[bold]Total Sessions:[/bold] {total_sessions}
[bold]Completed:[/bold] {completed_sessions}
[bold]Total Time:[/bold] {total_minutes} minutes ({total_minutes/60:.1f} hours)

[bold]By Language:[/bold]
"""
    for lang, count in sorted(languages.items()):
        stats += f"  {lang}: {count} sessions\n"
    
    if topics:
        stats += "\n[bold]Topics Covered:[/bold]\n"
        for topic, count in sorted(topics.items(), key=lambda x: -x[1])[:10]:
            stats += f"  {topic}: {count}\n"
    
    console.print(Panel(stats, title="📚 Learning Progress"))
    
    table = Table(title="Recent Learning Sessions")
    table.add_column("Date", style="yellow")
    table.add_column("Language", style="cyan")
    table.add_column("Topic", style="green")
    table.add_column("Duration", style="magenta")
    table.add_column("Status")
    
    sorted_events = sorted(events, key=lambda e: e.date, reverse=True)[:10]
    for event in sorted_events:
        status = "✅" if event.completed else "⏳"
        table.add_row(
            event.date,
            getattr(event, 'language', '-'),
            getattr(event, 'topic', '-') or '-',
            f"{event.duration_minutes}m",
            status
        )
    
    console.print(table)


@cli.command()
@click.option("--format", "-f", type=click.Choice(["markdown", "csv"]), default="markdown", help="Export format")
@click.option("--output", "-o", default="fireschedule_export.md", help="Output file path")
def notion_export(format: str, output: str):
    """Export events to Notion-compatible format.
    
    Export your schedule to Notion-importable markdown or CSV.
    Use 'markdown' format for direct Notion import.
    Use 'csv' for backup/analysis.
    """
    from src.integrations.notion import NotionExporter
    
    storage = MarkdownStorage()
    exporter = NotionExporter(storage)
    
    output_path = Path(output)
    
    if format == "markdown":
        count = exporter.export_to_markdown(output_path)
        click.echo(f"✓ Exported {count} event(s) to {output_path}")
        click.echo("  Import this file into Notion using: Import > Markdown")
    else:
        count = exporter.export_to_csv(output_path)
        click.echo(f"✓ Exported {count} event(s) to {output_path}")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--format", "-f", type=click.Choice(["csv"]), default="csv", help="Import format")
def notion_import(file_path: str, format: str):
    """Import events from Notion export.
    
    FILE_PATH: Path to the exported CSV file from Notion.
    
    Note: Notion exports must be in CSV format.
    """
    from src.integrations.notion import NotionImporter
    
    storage = MarkdownStorage()
    importer = NotionImporter(storage)
    
    input_path = Path(file_path)
    
    if format == "csv":
        count = importer.import_from_csv(input_path)
        click.echo(f"✓ Imported {count} event(s) from {input_path}")
    else:
        click.echo(f"Unsupported format: {format}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--credentials", "-c", default="credentials.json", help="Path to OAuth credentials file")
def gcal_auth(credentials: str):
    """Authenticate with Google Calendar.
    
    Run this command first to set up Google Calendar integration.
    You need to download OAuth credentials from Google Cloud Console.
    """
    from src.integrations.gcal import GoogleCalendarAuth
    from src.config import config
    
    config.load()
    gcal_config = config.data.get("gcal", {})
    
    auth = GoogleCalendarAuth(
        credentials_file=gcal_config.get("credentials_file", "credentials.json"),
        token_file=gcal_config.get("token_file", "token.json")
    )
    
    if auth.is_authenticated():
        click.echo("Already authenticated with Google Calendar.")
        return
    
    if not Path(credentials).exists():
        click.echo(f"Error: Credentials file '{credentials}' not found.")
        click.echo("\nTo get credentials:")
        click.echo("1. Go to https://console.cloud.google.com/")
        click.echo("2. Create a project and enable Google Calendar API")
        click.echo("3. Create OAuth 2.0 credentials (Desktop app)")
        click.echo(f"4. Download the credentials.json file to: {Path.cwd()}")
        sys.exit(1)
    
    if auth.authenticate(credentials):
        click.echo("✓ Successfully authenticated with Google Calendar!")
    else:
        click.echo("✗ Authentication failed.", err=True)
        sys.exit(1)


@cli.command()
@click.option("--days", "-d", default=7, type=int, help="Number of days ahead to fetch")
def gcal_pull(days: int):
    """Pull events from Google Calendar.
    
    Import events from your Google Calendar into FireSchedule.
    """
    from src.integrations.gcal import GoogleCalendarAuth, GoogleCalendarClient
    from src.config import config
    
    config.load()
    gcal_config = config.data.get("gcal", {})
    
    auth = GoogleCalendarAuth(
        credentials_file=gcal_config.get("credentials_file", "credentials.json"),
        token_file=gcal_config.get("token_file", "token.json")
    )
    
    if not auth.is_authenticated():
        click.echo("Not authenticated. Run 'fireschedule gcal-auth' first.", err=True)
        sys.exit(1)
    
    client = GoogleCalendarClient(
        auth,
        calendar_id=gcal_config.get("calendar_id", "primary")
    )
    
    storage = MarkdownStorage()
    events = client.pull_events(days_ahead=days)
    
    imported = 0
    for event in events:
        storage.save_event(event)
        imported += 1
    
    click.echo(f"✓ Pulled {imported} event(s) from Google Calendar")


@cli.command()
def gcal_push():
    """Push local events to Google Calendar.
    
    Export all local events to your Google Calendar.
    """
    from src.integrations.gcal import GoogleCalendarAuth, GoogleCalendarClient
    from src.config import config
    
    config.load()
    gcal_config = config.data.get("gcal", {})
    
    auth = GoogleCalendarAuth(
        credentials_file=gcal_config.get("credentials_file", "credentials.json"),
        token_file=gcal_config.get("token_file", "token.json")
    )
    
    if not auth.is_authenticated():
        click.echo("Not authenticated. Run 'fireschedule gcal-auth' first.", err=True)
        sys.exit(1)
    
    client = GoogleCalendarClient(
        auth,
        calendar_id=gcal_config.get("calendar_id", "primary")
    )
    
    storage = MarkdownStorage()
    events = []
    from src.models.events import Category
    for cat in Category:
        events.extend(storage.list_events(cat))
    
    exported = 0
    for event in events:
        if not hasattr(event, 'gcal_id') or not event.gcal_id:
            gcal_id = client.push_event(event)
            if gcal_id:
                event.gcal_id = gcal_id
                storage.save_event(event)
                exported += 1
    
    click.echo(f"✓ Pushed {exported} event(s) to Google Calendar")


@cli.command()
@click.option("--days", "-d", default=7, type=int, help="Number of days ahead to sync")
def gcal_sync(days: int):
    """Bi-directional sync with Google Calendar.
    
    Pull events from Google Calendar and push local events to Google Calendar.
    """
    from src.integrations.gcal import GoogleCalendarAuth, GoogleCalendarClient, SyncStatus
    from src.config import config
    
    config.load()
    gcal_config = config.data.get("gcal", {})
    
    auth = GoogleCalendarAuth(
        credentials_file=gcal_config.get("credentials_file", "credentials.json"),
        token_file=gcal_config.get("token_file", "token.json")
    )
    
    if not auth.is_authenticated():
        click.echo("Not authenticated. Run 'fireschedule gcal-auth' first.", err=True)
        sys.exit(1)
    
    client = GoogleCalendarClient(
        auth,
        calendar_id=gcal_config.get("calendar_id", "primary")
    )
    
    storage = MarkdownStorage()
    result = client.sync_events(storage, days_ahead=days)
    
    status = SyncStatus()
    status.update(imported=result["imported"], exported=result["exported"])
    
    click.echo(f"✓ Sync complete!")
    click.echo(f"  Imported from GCal: {result['imported']}")
    click.echo(f"  Exported to GCal: {result['exported']}")
    click.echo(f"  Total GCal events: {result['total_gcal']}")
    click.echo(f"  Total local events: {result['total_local']}")


@cli.command()
def gcal_status():
    """Show Google Calendar sync status."""
    from src.integrations.gcal import GoogleCalendarAuth, SyncStatus
    from src.config import config
    
    config.load()
    gcal_config = config.data.get("gcal", {})
    
    auth = GoogleCalendarAuth(
        credentials_file=gcal_config.get("credentials_file", "credentials.json"),
        token_file=gcal_config.get("token_file", "token.json")
    )
    
    click.echo("Google Calendar Status:")
    click.echo(f"  Authenticated: {'Yes' if auth.is_authenticated() else 'No'}")
    
    if auth.is_authenticated():
        status = SyncStatus()
        click.echo(f"  Last sync: {status.last_sync or 'Never'}")
        click.echo(f"  Status: {status.status}")


if __name__ == "__main__":
    cli()
