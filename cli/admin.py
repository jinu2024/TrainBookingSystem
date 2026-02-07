from __future__ import annotations
import sys

import questionary
from rich.console import Console
from rich.panel import Panel

from services import user as user_service
from services import train as train_service
from ui import messages

console = Console()


def register_admin(
    interactive: bool = True,
    username: str | None = None,
    email: str | None = None,
    password: str | None = None,
) -> dict:
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
        messages.show_success(
            f"Admin '{result['username']}' created (id={result['id']})"
        )
        return result
    except Exception as exc:  # keep narrow in real code; here we show errors to user
        messages.show_error(str(exc))
        raise


def admin_dashboard(username: str) -> None:
    """Admin dashboard — opens a connection and runs admin actions until logout.

    Uses an interactive selection (arrow keys) via questionary.select.
    """
    console.print(Panel(f"Admin Dashboard — {username}", style="bold magenta"))

    while True:
        choice = questionary.select(
            "Select admin action:",
            choices=[
                "Admin Train Registration",
                "Train Details Update",
                "Delete Train",
                "View All Trains",
                "Logout",
            ],
        ).ask()

        if choice == "Admin Train Registration":
            admin_train_registration()
            continue
        if choice == "Train Details Update":
            train_details_update()
            continue
        if choice == "Delete Train":
            delete_train_by_admin()
            continue
        if choice == "View All Trains":
            admin_view_all_trains()
            continue
        if choice == "Logout":
            messages.show_info("Logged out")
            return


# ================= ADMIN ACTIONS =================


def admin_train_registration() -> None:
    console.print("[cyan] Admin Train Registration[/cyan]")
    train_number = questionary.text("Train Number:").ask()
    train_name = questionary.text("Train Name:").ask()

    try:
        train_service.add_train(train_number, train_name)
        console.print("[bold green] Train Registered Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error registering train: {e}[/bold red]")


def train_details_update() -> None:
    console.print("[cyan] Update Train Details[/cyan]")
    train_id = questionary.text("Enter Train ID to update:").ask()
    new_name = questionary.text("New Train Name:").ask()

    try:
        train_service.update_train(int(train_id), new_name)
        console.print("[bold green] Train Updated Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error updating train: {e}[/bold red]")


def delete_train_by_admin() -> None:
    console.print("[cyan] Delete Train[/cyan]")
    train_id = questionary.text("Enter Train ID to delete:").ask()
    try:
        train_service.remove_train(int(train_id))
        console.print("[bold green]Train marked inactive[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error deleting train: {e}[/bold red]")


def admin_view_all_trains() -> None:
    console.print("[cyan] All Trains[/cyan]")
    rows = train_service.list_trains()

    if not rows:
        console.print("[yellow]No trains found[/yellow]")
        return

    for row in rows:
        console.print(row)


if __name__ == "__main__":
    # When run as script, go interactive
    try:
        register_admin()
    except Exception:
        pass
