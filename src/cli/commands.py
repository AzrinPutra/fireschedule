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
        event_type=EventType.GENERAL,
        date=date,
        time=time or "09:00",
        duration_minutes=duration,
        description=description,
        priority=Priority.MEDIUM,
    )
    
    storage.save(event)
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
    
    events = storage.load_all()
    
    if today:
        today_str = datetime.now().strftime("%Y-%m-%d")
        events = [e for e in events if e.date == today_str]
    elif week:
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        events = [e for e in events if today <= datetime.strptime(e.date, "%Y-%m-%d").date() < week_end]
    
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
            str(event.category.name),
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
    event = storage.load(event_id)
    
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
    
    storage.save(event)
    click.echo(f"✓ Event '{event_id}' updated successfully!")


@cli.command()
@click.argument("event_id")
def delete(event_id: str):
    """Delete an event."""
    success = storage.delete(event_id)
    
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


if __name__ == "__main__":
    cli()
