from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel

from ui import messages


def passenger_dashboard(username: str, session_token: str | None = None) -> None:
    """Simple passenger dashboard with logout option."""
    console = Console()
    console.print(Panel(f"Passenger Dashboard — {username}", style="bold blue"))

    # check session validity if provided
    if session_token:
        try:
            from services import session as session_service

            session_service.validate_session(session_token)
        except Exception:
            messages.show_error("Session expired or invalid. Logged out.")
            return

    while True:
        # show simple actions ; keep session active until Logout
        choice = questionary.select("Passenger actions:", choices=["Logout"]).ask()
        if choice == "Logout":
            # invalidate session if present
            if session_token:
                from services import session as session_service

                try:
                    session_service.invalidate_session(session_token)
                except Exception:
                    pass
            messages.show_info("Logged out")
            return


if __name__ == "__main__":
    # quick manual test
    passenger_dashboard("demo_passenger")


def register_customer(interactive: bool = True, username: str | None = None, email: str | None = None, password: str | None = None) -> dict:
    """Register a new customer (passenger).

    Mirrors the admin registration flow but uses `create_customer` service.
    """
    console = Console()
    console.print(Panel("Passenger Registration", style="bold blue", expand=False))

    if interactive:
        username = questionary.text("Username:").ask()
        email = questionary.text("Email:").ask()
        password = questionary.password("Password (min 8 chars):").ask()

    try:
        from services.user import create_customer

        result = create_customer(username, email, password)
        messages.show_success(f"Customer '{result['username']}' created (id={result['id']})")
        return result
    except Exception as exc:
        messages.show_error(str(exc))
        raise
