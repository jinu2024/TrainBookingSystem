from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel

from ui import messages


def passenger_dashboard(username: str) -> None:
    """Simple passenger dashboard with logout option."""
    console = Console()
    console.print(Panel(f"Passenger Dashboard — {username}", style="bold blue"))

    while True:
        choice = questionary.select("Passenger actions:", choices=["Logout"]).ask()
        if choice == "Logout":
            messages.show_info("Logged out")
            return


if __name__ == "__main__":
    # quick manual test
    passenger_dashboard("demo_passenger")
