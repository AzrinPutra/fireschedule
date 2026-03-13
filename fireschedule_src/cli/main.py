"""FireSchedule CLI Entry Point."""

import sys
from pathlib import Path

fireschedule_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(fireschedule_dir))

from fireschedule_src.cli.commands import cli


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
