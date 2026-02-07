import sys
import os
import sqlite3
import questionary
from rich.console import Console
from rich.panel import Panel


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import query helpers
from database.queries import (
    get_user_by_username,
    get_all_trains,
    create_train,
    delete_train,
)
from utils.security import verify_password

console = Console()


# ================= ADMIN LOGIN =================

def admin_login(conn: sqlite3.Connection) -> None:
    console.print(Panel("Admin Login", style="bold cyan", expand=False))

    username = questionary.text("Username:").ask()
    password = questionary.password("Password:").ask()

    user = get_user_by_username(conn, username)

    if not user:
        _invalid_login()
        return

    db_password = user[3]   # password hash
    role = user[4]          # role

    if role != "admin" or not verify_password(password, db_password):
        _invalid_login()
        return

    console.print("[bold green] Login Successful! Welcome Admin[/bold green]")
    admin_dashboard(conn)


def _invalid_login() -> None:
    console.print("[bold red] Invalid Username or Password[/bold red]")


# ================= ADMIN DASHBOARD =================

def admin_dashboard(conn: sqlite3.Connection) -> None:
    while True:
        console.print(
            Panel(
                "\n".join([
                    " Admin Dashboard",
                    "1) Admin Train Registration",
                    "2) Train Details Update",
                    "3) Delete Train",
                    "4) View All Trains",
                    "5) Exit"
                ]),
                style="bold green",
                expand=False
            )
        )

        choice = questionary.text("Select option (1-5):").ask()

        match choice:
            case "1":
                admin_train_registration(conn)
            case "2":
                train_details_update(conn)
            case "3":
                delete_train_by_admin(conn)
            case "4":
                admin_view_all_trains(conn)
            case "5":
                console.print("[bold yellow] Exiting Admin Panel[/bold yellow]")
                sys.exit(0)
            case _:
                console.print("[bold red] Invalid choice. Select 1–5[/bold red]")


# ================= ADMIN ACTIONS =================

def admin_train_registration(conn: sqlite3.Connection) -> None:
    console.print("[cyan] Admin Train Registration[/cyan]")
    train_number = questionary.text("Train Number:").ask()
    train_name = questionary.text("Train Name:").ask()

    try:
        create_train(conn, train_number, train_name)
        console.print("[bold green] Train Registered Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error registering train: {e}[/bold red]")


def train_details_update(conn: sqlite3.Connection) -> None:
    console.print("[cyan] Update Train Details[/cyan]")
    train_id = questionary.text("Enter Train ID to update:").ask()
    new_name = questionary.text("New Train Name:").ask()

    try:
        cur = conn.cursor()
        cur.execute("UPDATE trains SET train_name = ? WHERE id = ?", (new_name, train_id))
        conn.commit()
        console.print("[bold green] Train Updated Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error updating train: {e}[/bold red]")


def delete_train_by_admin(conn: sqlite3.Connection) -> None:
    console.print("[cyan] Delete Train[/cyan]")
    train_id = questionary.text("Enter Train ID to delete:").ask()

    try:
        delete_train(conn, train_id)
        console.print("[bold green]Train marked inactive[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error deleting train: {e}[/bold red]")


def admin_view_all_trains(conn: sqlite3.Connection) -> None:
    console.print("[cyan] All Trains[/cyan]")
    rows = get_all_trains(conn)

    if not rows:
        console.print("[yellow]No trains found[/yellow]")
        return

    for row in rows:
        console.print(row)


# ================= ENTRY POINT =================

def main():
    conn = sqlite3.connect("database.db")
    admin_login(conn)


if __name__ == "__main__":
    main()

