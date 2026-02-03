from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel

from services import user as user_service
from ui import messages

console = Console()


def register_admin(interactive: bool = True, username: str | None = None, email: str | None = None, password: str | None = None) -> dict:
    """Register a new admin.

    If `interactive` is True (default) the function will prompt the user using
    `questionary` and display output via `rich` (wrapped in `ui/messages`). For
    programmatic use set `interactive=False` and pass the fields directly.
    """
    # Header
    console.print(Panel("Admin Registration", style="bold cyan", expand=False))

    if interactive:
        username = questionary.text("Username:").ask()
        email = questionary.text("Email:").ask()
        password = questionary.password("Password (min 8 chars):").ask()

    # Basic guard - services will validate more thoroughly and raise ValueError
    try:
        result = user_service.create_admin(username, email, password)
        messages.show_success(f"Admin '{result['username']}' created (id={result['id']})")
        return result
    except Exception as exc:  # keep narrow in real code; here we show errors to user
        messages.show_error(str(exc))
        raise


if __name__ == "__main__":
    # When run as script, go interactive
    try:
        register_admin()
    except Exception:
        pass
