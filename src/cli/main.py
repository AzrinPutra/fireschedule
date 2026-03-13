"""FireSchedule CLI Entry Point."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.commands import cli


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
