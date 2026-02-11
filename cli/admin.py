from __future__ import annotations
from collections import defaultdict
from datetime import datetime
import sys

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


from services import user as user_service
from services import schedule as schedule_service
from services import station as station_service
from services import train as train_service
from ui import messages
from utils.__helper import ask_required, ask_with_validation
from utils.validators import (
    is_valid_station_code,
    is_valid_train_number,
    is_valid_schedule_date,
    is_valid_time,
    is_valid_fare,
)

console = Console()


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
                "Delete Train Journey",
                "View All Trains",
                "View All Stations",
                "View All Train Jouneys",
                "View Train Route by Train",
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
            train_journey_details_update()
            continue
        if choice == "Delete Train Journey":
            delete_train_journey_by_admin()
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
        if choice == "View Train Route by Train":
            admin_view_train_route_by_train()
            continue
        if choice == "Logout":
            messages.show_info("Logged out")
            return


# ================= ADMIN ACTIONS =================


def admin_train_registration() -> None:
    console.print("[cyan] Admin Train Registration[/cyan]")

    train_number = ask_with_validation(
        "Train Number (6 digits):",
        validator=is_valid_train_number,
        error_msg="Train Number must be exactly 6 digits",
        attempts=3,
    )
    if train_number is None:
        return

    train_name = ask_required("Train Name:")
    if train_name is None:
        return

    try:
        train_service.add_train(train_number, train_name)
        console.print("[bold green] Train Registered Successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error registering train: {e}[/bold red]")


def admin_add_station() -> None:
    console.print("[cyan] Add Station[/cyan]")

    code = ask_with_validation(
        "Station Code (6 characters):",
        validator=is_valid_station_code,
        error_msg="Station Code must be exactly 6 characters (uppercase letters and digits)",
        attempts=3,
    )
    if code is None:
        return

    name = ask_required("Station name:")
    if name is None:
        return

    city = ask_required("City:")
    if city is None:
        return

    try:
        from services import station as station_service

        station_service.add_station(code, name, city)
        console.print("[bold green] Station added successfully[/bold green]")
    except Exception as e:
        console.print(f"[bold red] Error adding station: {e}[/bold red]")


def admin_schedule_new_train_jouney() -> None:
    console.print("[cyan] Schedule New Train Journey[/cyan]")

    from datetime import datetime
    from services import station as station_service
    from services import schedule as schedule_service

    rows = train_service.list_trains()
    if not rows:
        console.print("[yellow]No trains available[/yellow]")
        return

    train_map = {
        f"{r['id']} - {r['train_number']} - {r['train_name']}": r["id"] for r in rows
    }

    train_choice = questionary.select("Select train:", choices=list(train_map)).ask()
    if not train_choice:
        raise SystemExit

    train_id = train_map[train_choice]

    stations = station_service.list_stations()
    station_map = {f"{s['id']} - {s['code']} - {s['name']}": s["id"] for s in stations}

    origin_choice = questionary.select(
        "Origin station:", choices=list(station_map)
    ).ask()
    if not origin_choice:
        raise SystemExit

    dest_choice = questionary.select(
        "Destination station:",
        choices=[c for c in station_map if c != origin_choice],
    ).ask()
    if not dest_choice:
        raise SystemExit

    origin_id = station_map[origin_choice]
    dest_id = station_map[dest_choice]

    # ---------- Required Validated Inputs ----------
    departure_date = ask_with_validation(
        "Departure Date (YYYY-MM-DD):",
        validator=is_valid_schedule_date,
        error_msg="Invalid date",
        attempts=3,
    )
    if departure_date is None:
        return

    arrival_date = ask_with_validation(
        "Arrival Date (YYYY-MM-DD):",
        validator=is_valid_schedule_date,
        error_msg="Invalid date",
        attempts=3,
    )
    if arrival_date is None:
        return

    departure_time = ask_with_validation(
        "Departure Time (HH:MM):",
        validator=is_valid_time,
        error_msg="Invalid time",
        attempts=3,
    )
    if departure_time is None:
        return

    arrival_time = ask_with_validation(
        "Arrival Time (HH:MM):",
        validator=is_valid_time,
        error_msg="Invalid time",
        attempts=3,
    )
    if arrival_time is None:
        return

    fare_input = ask_with_validation(
        "Fare (₹):",
        validator=is_valid_fare,
        error_msg="Fare must be positive number",
        attempts=3,
    )
    if fare_input is None:
        return

    fare = float(fare_input)

    # ---------- Final logic check ----------
    dep_dt = datetime.strptime(f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M")
    arr_dt = datetime.strptime(f"{arrival_date} {arrival_time}", "%Y-%m-%d %H:%M")

    if arr_dt <= dep_dt:
        messages.show_error("Arrival must be after departure")
        return

    try:
        sched_id = schedule_service.create_schedule(
            train_id,
            origin_id,
            dest_id,
            departure_date,
            arrival_date,
            departure_time,
            arrival_time,
            fare,
        )

        console.print(f"[bold green]Schedule created (id={sched_id})[/bold green]")

    except Exception as e:
        console.print(f"[bold red] Error creating schedule: {e}[/bold red]")


def train_details_update() -> None:
    console.print("[cyan]Update Train Details[/cyan]")

    train_id = ask_required(
        "Enter Train number to update:",
        validator=is_valid_train_number,
        error_msg="Invalid train number",
        attempts=3,
    )

    new_name = ask_required("New Train Name:")

    try:
        train_service.update_train(int(train_id), new_name)
        console.print("[bold green]Train Updated Successfully[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error updating train: {e}[/bold red]")


def station_details_update() -> None:
    console.print("[cyan]Update Station Details[/cyan]")

    station_id = ask_required(
        "Enter Station code to update:",
        validator=is_valid_station_code,
        error_msg="Station Code must be 6 uppercase letters/digits",
        attempts=3,
    )

    new_name = ask_required("New Station Name:")

    try:
        station_service.update_station(station_id, new_name)
        console.print("[bold green]Station Updated Successfully[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error updating station: {e}[/bold red]")


def train_journey_details_update() -> None:
    console.print("[cyan]Update Train Journey Details[/cyan]")

    rows = schedule_service.list_schedules()

    if not rows:
        console.print("[yellow]No train journeys available[/yellow]")
        return

    # ================= SELECT JOURNEY =================
    journey_map = {}

    for r in rows:
        display = (
            f"{r['id']} | Train:{r['train_id']} | "
            f"{r['origin_station_id']}->{r['destination_station_id']} | "
            f"{r['departure_date']} {r['departure_time']}"
        )
        journey_map[display] = r

    choice = questionary.select(
        "Select journey to update:",
        choices=list(journey_map.keys()),
    ).ask()

    if not choice:
        return

    current = journey_map[choice]

    schedule_id = current["id"]
    train_id = current["train_id"]

    origin_id = current["origin_station_id"]
    dest_id = current["destination_station_id"]

    departure_date = current["departure_date"]
    arrival_date = current["arrival_date"]

    departure_time = current["departure_time"]
    arrival_time = current["arrival_time"]

    fare = current["fare"]

    console.print("\n[yellow]Press ENTER to keep existing value[/yellow]\n")

    # ================= STATIONS =================
    stations = station_service.list_stations()

    station_map = {f"{s['id']} - {s['code']} - {s['name']}": s["id"] for s in stations}

    station_choices = list(station_map.keys())

    origin_choice = questionary.select(
        f"Origin station [current: {origin_id}]",
        choices=["<keep current>"] + station_choices,
    ).ask()

    if origin_choice != "<keep current>":
        origin_id = station_map[origin_choice]

    dest_choice = questionary.select(
        f"Destination station [current: {dest_id}]",
        choices=["<keep current>"] + station_choices,
    ).ask()

    if dest_choice != "<keep current>":
        dest_id = station_map[dest_choice]

    # ================= DATES =================
    new_dep_date = questionary.text(
        f"Departure date (YYYY-MM-DD) [{departure_date}]:"
    ).ask()

    new_arr_date = questionary.text(
        f"Arrival date (YYYY-MM-DD) [{arrival_date}]:"
    ).ask()

    if new_dep_date:
        if not is_valid_schedule_date(new_dep_date):
            console.print("[red]Invalid departure date[/red]")
            return
        departure_date = new_dep_date

    if new_arr_date:
        if not is_valid_schedule_date(new_arr_date):
            console.print("[red]Invalid arrival date[/red]")
            return
        arrival_date = new_arr_date

    # ================= TIMES =================
    new_dep = questionary.text(f"Departure time (HH:MM) [{departure_time}]:").ask()

    new_arr = questionary.text(f"Arrival time (HH:MM) [{arrival_time}]:").ask()

    if new_dep:
        if not is_valid_time(new_dep):
            console.print("[red]Invalid departure time[/red]")
            return
        departure_time = new_dep

    if new_arr:
        if not is_valid_time(new_arr):
            console.print("[red]Invalid arrival time[/red]")
            return
        arrival_time = new_arr

    # ================= FARE =================
    new_fare = questionary.text(f"Fare [{fare}]:").ask()

    if new_fare:
        try:
            new_fare = float(new_fare)
            if new_fare < 0:
                raise ValueError
            fare = new_fare
        except:
            console.print("[red]Invalid fare amount[/red]")
            return

    # ================= UPDATE =================
    try:
        schedule_service.update_schedule(
            schedule_id,
            train_id,
            origin_id,
            dest_id,
            departure_date,
            arrival_date,
            departure_time,
            arrival_time,
            fare,
        )

        console.print("[bold green]Train Journey Updated Successfully[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error updating journey: {e}[/bold red]")

def delete_train_journey_by_admin() -> None:
    console.print("[cyan] Delete Train Journey[/cyan]")

    try:
        from services import schedule as schedule_service
        from services import train as train_service
        from services import station as station_service
    except Exception as e:
        console.print(f"[bold red] Import error: {e}[/bold red]")
        return

    # ================= LIST SCHEDULES =================
    rows = schedule_service.list_schedules()

    if not rows:
        console.print("[yellow]No train journeys available[/yellow]")
        return

    # ================= LOAD TRAIN DATA =================
    trains = train_service.list_trains()
    train_lookup = {
        t["id"]: f"{t['train_number']} - {t['train_name']}"
        for t in trains
    }

    # ================= LOAD STATION DATA =================
    stations = station_service.list_stations()
    station_lookup = {
        s["id"]: f"{s['code']} - {s['name']}"
        for s in stations
    }

    schedule_map = {}
    choices = []

    for r in rows:
        train_display = train_lookup.get(r["train_id"], str(r["train_id"]))
        origin_display = station_lookup.get(
            r["origin_station_id"], str(r["origin_station_id"])
        )
        dest_display = station_lookup.get(
            r["destination_station_id"], str(r["destination_station_id"])
        )

        display = (
            f"{r['id']} | "
            f"{train_display} | "
            f"{origin_display} → {dest_display} | "
            f"{r['departure_date']} {r['departure_time']} → "
            f"{r['arrival_date']} {r['arrival_time']} | ₹{r['fare']}"
        )

        schedule_map[display] = r["id"]
        choices.append(display)

    # ================= SELECT =================
    selected = questionary.select(
        "Select journey to delete:",
        choices=choices,
    ).ask()

    if not selected:
        return

    schedule_id = schedule_map[selected]

    # ================= CONFIRM =================
    confirm = questionary.confirm(
        f"Are you sure you want to delete schedule ID {schedule_id}?",
        default=False,
    ).ask()

    if not confirm:
        console.print("[yellow]Deletion cancelled[/yellow]")
        return

    # ================= DELETE =================
    try:
        schedule_service.delete_schedule(schedule_id)
        console.print("[bold green] Train Journey deleted successfully[/bold green]")

    except Exception as e:
        console.print(f"[bold red] Error deleting train journey: {e}[/bold red]")


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
        from services import station as station_service
        from services import train as train_service

        rows = schedule_service.list_schedules()

        if not rows:
            console.print("[yellow]No train journeys found[/yellow]")
            return

        # ================= LOOKUPS =================
        trains = train_service.list_trains()
        stations = station_service.list_stations()

        train_lookup = {
            t["id"]: f"{t['train_number']} - {t['train_name']}" for t in trains
        }
        station_lookup = {s["id"]: s["name"] for s in stations}

        # ================= SORT =================
        rows.sort(
            key=lambda r: (
                r["train_id"],
                r["departure_date"],
                r["departure_time"],
            )
        )

        # ================= TABLE =================
        table = Table(show_header=True, header_style="bold magenta")

        table.add_column("ID", style="dim")
        table.add_column("Train")
        table.add_column("From")
        table.add_column("To")
        table.add_column("Dep Date")
        table.add_column("Dep Time")
        table.add_column("Arr Date")
        table.add_column("Arr Time")
        table.add_column("Fare")

        seen = set()  # protect against real duplicates

        for r in rows:

            unique_key = (
                r["train_id"],
                r["origin_station_id"],
                r["destination_station_id"],
                r["departure_date"],
                r["departure_time"],
            )

            if unique_key in seen:
                continue
            seen.add(unique_key)

            table.add_row(
                str(r["id"]),
                train_lookup.get(r["train_id"], str(r["train_id"])),
                station_lookup.get(r["origin_station_id"], str(r["origin_station_id"])),
                station_lookup.get(
                    r["destination_station_id"], str(r["destination_station_id"])
                ),
                r["departure_date"],
                r["departure_time"],
                r["arrival_date"],
                r["arrival_time"],
                f"₹{r['fare']}",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red] Error Viewing Train Journeys: {e}[/bold red]")


def admin_view_train_route_by_train() -> None:
    console.print("[cyan] View Train Route by Train[/cyan]")

    rows = train_service.list_trains()

    if not rows:
        console.print("[yellow]No trains available[/yellow]")
        return

    train_map = {
        f"{r['id']} - {r['train_number']} - {r['train_name']}": r["id"] for r in rows
    }

    train_choice = questionary.select(
        "Select Train:",
        choices=list(train_map.keys()),
    ).ask()

    if not train_choice:
        return

    train_id = train_map[train_choice]

    try:
        schedules = schedule_service.get_schedules_by_train(train_id)

        if not schedules:
            console.print("[yellow]No journeys found for this train[/yellow]")
            return

        stations = station_service.list_stations()
        station_lookup = {s["id"]: s["name"] for s in stations}

        # ================= REMOVE DUPLICATES =================
        unique = {}
        for r in schedules:
            key = (
                r["origin_station_id"],
                r["destination_station_id"],
                r["departure_date"],
                r["departure_time"],
                r["arrival_time"],
            )
            unique[key] = r

        schedules = list(unique.values())

        # ================= GROUP BY DATE =================
        grouped = defaultdict(list)

        for r in schedules:
            dep_dt = datetime.strptime(
                f"{r['departure_date']} {r['departure_time']}",
                "%Y-%m-%d %H:%M",
            )
            grouped[r["departure_date"]].append((dep_dt, r))

        console.print(f"\n[bold green]{train_choice}[/bold green]\n")

        # ================= DISPLAY =================
        for date in sorted(grouped.keys()):

            items = grouped[date]
            items.sort(key=lambda x: x[0])

            table = Table(show_header=True, header_style="bold magenta")
            table.title = f"Date: {date}"

            table.add_column("From", style="cyan")
            table.add_column("To", style="cyan")
            table.add_column("Departure")
            table.add_column("Arrival")
            table.add_column("Fare")

            route_chain = []

            for _, r in items:
                origin = station_lookup.get(r["origin_station_id"])
                dest = station_lookup.get(r["destination_station_id"])

                table.add_row(
                    origin,
                    dest,
                    r["departure_time"],
                    r["arrival_time"],
                    f"₹{r['fare']}",
                )

                if not route_chain:
                    route_chain.append(origin)

                # avoid repeated chain nodes
                if route_chain[-1] != dest:
                    route_chain.append(dest)

            console.print(table)

            console.print(
                "[bold yellow]Full Route:[/bold yellow] "
                + " → ".join(route_chain)
                + "\n"
            )

    except Exception as e:
        console.print(f"[bold red] Error Viewing Train Routes: {e}[/bold red]")
