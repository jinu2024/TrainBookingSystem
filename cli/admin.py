from __future__ import annotations
import sys

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


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
                "Add new Train",
                "Add new Station",
                "Schedule new Train Jouney",
                "Update exisitng Train",
                "Update existing Station",
                "Update existing Train Journey",
                "Delete Train",
                "View All Trains",
                "View All Stations",
                "View All Train Jouneys",
                "Logout",
            ],
        ).ask()

        if choice == "Add new Train":
            admin_train_registration()
            continue
        if choice == "Add new Station":
            admin_add_station()
            continue
        if choice == "Schedule new Train Jouney":
            admin_schedule_new_train_jouney()
            continue
        if choice == "Update exisitng Train":
            train_details_update()
            continue
        if choice == "Update existing Station":
            station_details_update()
            continue
        if choice == "Update existing Train Journey":
            train_journey_details_update
            continue
        if choice == "Delete Train":
            delete_train_by_admin()
            continue
        if choice == "View All Trains":
            admin_view_all_trains()
            continue
        if choice == "View All Stations":
            admin_view_all_stations()
            continue
        if choice == "View All Train Jouneys":
            admin_view_all_train_jouneys()
            continue
        if choice == "Logout":
            messages.show_info("Logged out")
            return


# ================= ADMIN ACTIONS =================


def admin_train_registration() -> None:
    console.print("[cyan] Admin Train Registration[/cyan]")
    train_number = questionary.text("Train Number (6 char):").ask()
    train_name = questionary.text("Train Name:").ask()

    try:
        train_service.add_train(train_number, train_name)
        console.print("[bold green] Train Registered Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error registering train: {e}[/bold red]")


def admin_add_station() -> None:
    console.print("[cyan] Add Station[/cyan]")
    code = questionary.text("Station code (6 char):").ask()
    name = questionary.text("Station name:").ask()
    city = questionary.text("City:").ask()

    try:
        # import station service lazily to avoid circular imports
        from services import station as station_service

        station_service.add_station(code, name, city)
        console.print("[bold green] Station added successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error adding station: {e}[/bold red]")


def admin_schedule_new_train_jouney() -> None:
    console.print("[cyan] Schedule New Train Journey[/cyan]")

    # list trains
    rows = train_service.list_trains()
    if not rows:
        console.print("[yellow]No trains available to schedule[/yellow]")
        return

    train_map = {}
    train_choices = []
    for r in rows:
        # r may be sqlite3.Row or tuple
        try:
            tid = r["id"]
            tnum = r["train_number"]
            tname = r["train_name"]
        except Exception:
            tid = r[0]
            tnum = r[1]
            tname = r[2]

        display = f"{tid} - {tnum} - {tname}"
        train_map[display] = tid
        train_choices.append(display)

    train_choice = questionary.select("Select train:", choices=train_choices).ask()
    if not train_choice:
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    train_id = int(train_map[train_choice])

    # list stations
    try:
        from services import station as station_service

        stations = station_service.list_stations()
    except Exception as e:
        console.print(f"[bold red] Error fetching stations: {e}[/bold red]")
        return

    if not stations:
        console.print("[yellow]No stations available. Add stations first.[/yellow]")
        return

    station_map = {}
    station_choices = []
    for s in stations:
        try:
            sid = s["id"]
            scode = s["code"]
            sname = s["name"]
        except Exception:
            sid = s[0]
            scode = s[1]
            sname = s[2]

        display = f"{sid} - {scode} - {sname}"
        station_map[display] = sid
        station_choices.append(display)

    origin_choice = questionary.select(
        "Select origin station:", choices=station_choices
    ).ask()
    if not origin_choice:
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    origin_id = int(station_map[origin_choice])

    # choose destination (prevent same as origin)
    dest_choices = [c for c in station_choices if c != origin_choice]
    if not dest_choices:
        console.print(
            "[yellow]Need at least two stations to schedule a journey[/yellow]"
        )
        return

    dest_choice = questionary.select(
        "Select destination station:", choices=dest_choices
    ).ask()
    if not dest_choice:
        console.print("[yellow]Operation cancelled[/yellow]")
        return
    dest_id = int(station_map[dest_choice])

    # times and date
    travel_date = questionary.text("Travel date (YYYY-MM-DD):").ask()
    departure_time = questionary.text("Departure time (HH:MM):").ask()
    arrival_time = questionary.text("Arrival time (HH:MM):").ask()

    # validate simple formats
    from datetime import datetime

    try:
        datetime.strptime(travel_date, "%Y-%m-%d")
        datetime.strptime(departure_time, "%H:%M")
        datetime.strptime(arrival_time, "%H:%M")
    except Exception:
        console.print(
            "[bold red]Invalid date/time format. Use YYYY-MM-DD and HH:MM[/bold red]"
        )
        return

    try:
        from services import schedule as schedule_service

        sched_id = schedule_service.create_schedule(
            train_id,
            origin_id,
            dest_id,
            travel_date,
            departure_time,
            arrival_time,
        )
        console.print(f"[bold green]Schedule created (id={sched_id})[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error creating schedule: {e}[/bold red]")


def train_details_update() -> None:
    console.print("[cyan] Update Train Details[/cyan]")
    train_id = questionary.text("Enter Train number to update:").ask()
    new_name = questionary.text("New Train Name:").ask()

    try:
        train_service.update_train(int(train_id), new_name)
        console.print("[bold green] Train Updated Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error updating train: {e}[/bold red]")


def station_details_update() -> None:
    console.print("[cyan] Update Station Details[/cyan]")
    station_id: int = questionary.text("Enter Station number to update:").ask()
    new_name: str = questionary.text("New Station Name:").ask()

    try:
        from services import station as station_service

        station_service.update_station(station_id, new_name)
        console.print("[bold green] Station Updated Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error updating Station details: {e}[/bold red]")


def train_journey_details_update() -> None:
    console.print("[cyan] Update Train Journey Details[/cyan]")

    try:
        from services import schedule as schedule_service
        from services import station as station_service
    except Exception as e:
        console.print(f"[bold red] Import error: {e}[/bold red]")
        return

    # ================= LIST JOURNEYS =================
    rows = schedule_service.list_schedules()

    if not rows:
        console.print("[yellow]No train journeys available[/yellow]")
        return

    journey_map = {}
    journey_choices = []

    for r in rows:
        try:
            jid = r["id"]
            train = r["train_id"]
            origin = r["origin_id"]
            dest = r["destination_id"]
            date = r["travel_date"]
        except Exception:
            jid, train, origin, dest, date = r[:5]

        display = f"{jid} | Train:{train} | {origin}->{dest} | {date}"
        journey_map[display] = jid
        journey_choices.append(display)

    choice = questionary.select(
        "Select journey to update:",
        choices=journey_choices,
    ).ask()

    if not choice:
        console.print("[yellow]Operation cancelled[/yellow]")
        return

    schedule_id = journey_map[choice]

    # ================= STATIONS =================
    stations = station_service.list_stations()

    station_map = {}
    station_choices = []

    for s in stations:
        try:
            sid = s["id"]
            code = s["code"]
            name = s["name"]
        except Exception:
            sid, code, name = s[:3]

        display = f"{sid} - {code} - {name}"
        station_map[display] = sid
        station_choices.append(display)

    origin_choice = questionary.select(
        "New origin station:",
        choices=station_choices,
    ).ask()

    dest_choice = questionary.select(
        "New destination station:",
        choices=[c for c in station_choices if c != origin_choice],
    ).ask()

    origin_id = station_map[origin_choice]
    dest_id = station_map[dest_choice]

    # ================= DATE/TIME =================
    travel_date = questionary.text("Travel date (YYYY-MM-DD):").ask()
    departure_time = questionary.text("Departure time (HH:MM):").ask()
    arrival_time = questionary.text("Arrival time (HH:MM):").ask()

    from datetime import datetime

    try:
        datetime.strptime(travel_date, "%Y-%m-%d")
        datetime.strptime(departure_time, "%H:%M")
        datetime.strptime(arrival_time, "%H:%M")
    except Exception:
        console.print(
            "[bold red]Invalid date/time format. Use YYYY-MM-DD and HH:MM[/bold red]"
        )
        return

    # ================= UPDATE =================
    try:
        schedule_service.update_schedule(
            schedule_id,
            train,
            origin_id,
            dest_id,
            travel_date,
            departure_time,
            arrival_time,
        )

        console.print("[bold green] Train Journey Updated Successfully[/bold green]")

    except Exception as e:
        console.print(f"[bold red] Error updating journey: {e}[/bold red]")


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

    table = Table(show_header=True, header_style="bold magenta")

    table.add_column("ID")
    table.add_column("Train Number")
    table.add_column("Train Name")
    table.add_column("Status")

    for r in rows:
        try:
            table.add_row(
                str(r["id"]),
                str(r["train_number"]),
                str(r["train_name"]),
                str(r["status"]),
            )
        except Exception:
            # fallback if tuple
            table.add_row(*[str(x) for x in r])

    console.print(table)

def admin_view_all_stations() -> None:
    console.print("[cyan] All Stations[/cyan]")

    try:
        from services import station as station_service

        rows = station_service.list_stations()

        if not rows:
            console.print("[yellow]No stations found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")

        table.add_column("ID")
        table.add_column("Code")
        table.add_column("Name")
        table.add_column("City")

        for r in rows:
            try:
                table.add_row(
                    str(r["id"]),
                    str(r["code"]),
                    str(r["name"]),
                    str(r["city"]),
                )
            except Exception:
                table.add_row(*[str(x) for x in r])

        console.print(table)

    except Exception as e:
        console.print(f"[bold red] Error Viewing Stations: {e}[/bold red]")


def admin_view_all_train_jouneys() -> None:
    console.print("[cyan] All Train Journeys[/cyan]")

    try:
        from services import schedule as schedule_service

        rows = schedule_service.list_schedules()

        if not rows:
            console.print("[yellow]No train journeys found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")

        table.add_column("ID")
        table.add_column("Train")
        table.add_column("Origin")
        table.add_column("Destination")
        table.add_column("Date")
        table.add_column("Departure")
        table.add_column("Arrival")

        for r in rows:
            try:
                table.add_row(
                    str(r["id"]),
                    str(r["train_id"]),
                    str(r["origin_station_id"]),
                    str(r["destination_station_id"]),
                    str(r["travel_date"]),
                    str(r["departure_time"]),
                    str(r["arrival_time"]),
                )
            except Exception:
                table.add_row(*[str(x) for x in r])

        console.print(table)

    except Exception as e:
        console.print(f"[bold red] Error Viewing Train Journeys: {e}[/bold red]")



if __name__ == "__main__":
    # When run as script, go interactive
    try:
        register_admin()
    except Exception:
        pass
