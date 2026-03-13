"""FireSchedule - TUI-based personal scheduling assistant."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import config
from src.models.events import Category, BaseEvent, LearningEvent
from src.storage.markdown import MarkdownStorage


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FireSchedule - Personal Scheduling Assistant")
    parser.add_argument("--tui", action="store_true", help="Launch TUI interface")
    args = parser.parse_args()

    config.load()

    if args.tui:
        from src.tui.app import FireScheduleApp
        app = FireScheduleApp()
        app.run()
    else:
        print("FireSchedule initialized")
        print(f"Categories: {list(config.categories.keys())}")
        print("Use --tui to launch the TUI interface")


if __name__ == "__main__":
    main()
