from __future__ import annotations
from collections import defaultdict
import sys

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table


from services import user as user_service
from services import train as train_service
from ui import messages

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
                "Delete Train",
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
        if choice == "View Train Route by Train":
            admin_view_train_route_by_train()
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

    # ================= TRAINS =================
    rows = train_service.list_trains()
    if not rows:
        console.print("[yellow]No trains available to schedule[/yellow]")
        return

    train_map = {}
    train_choices = []

    for r in rows:
        tid = r["id"]
        display = f"{tid} - {r['train_number']} - {r['train_name']}"
        train_map[display] = tid
        train_choices.append(display)

    train_choice = questionary.select("Select train:", choices=train_choices).ask()
    if not train_choice:
        return

    train_id = train_map[train_choice]

    # ================= STATIONS =================
    from services import station as station_service

    stations = station_service.list_stations()

    station_map = {}
    station_choices = []

    for s in stations:
        display = f"{s['id']} - {s['code']} - {s['name']}"
        station_map[display] = s["id"]
        station_choices.append(display)

    origin_choice = questionary.select(
        "Select origin station:", choices=station_choices
    ).ask()
    origin_id = station_map[origin_choice]

    dest_choice = questionary.select(
        "Select destination station:",
        choices=[c for c in station_choices if c != origin_choice],
    ).ask()
    dest_id = station_map[dest_choice]

    # ================= SMART SUGGESTIONS =================
    from services import schedule as schedule_service

    schedules = schedule_service.list_schedules()

    existing_dates = set()
    existing_dep = set()
    existing_arr = set()

    for s in schedules:
        if s["train_id"] == train_id:
            existing_dates.add(s["travel_date"])
            existing_dep.add(s["departure_time"])
            existing_arr.add(s["arrival_time"])

    console.print("\n[yellow]Select from existing or choose manual entry[/yellow]\n")

    # ---------- DATE ----------
    date_choice = questionary.select(
        "Travel Date:",
        choices=sorted(existing_dates) + ["<Enter new date>"],
    ).ask()

    if date_choice == "<Enter new date>":
        travel_date = questionary.text("Enter new date (YYYY-MM-DD):").ask()
    else:
        travel_date = date_choice

    # ---------- DEPARTURE ----------
    dep_choice = questionary.select(
        "Departure Time:",
        choices=sorted(existing_dep) + ["<Enter new time>"],
    ).ask()

    if dep_choice == "<Enter new time>":
        departure_time = questionary.text("Enter departure (HH:MM):").ask()
    else:
        departure_time = dep_choice

    # ---------- ARRIVAL ----------
    arr_choice = questionary.select(
        "Arrival Time:",
        choices=sorted(existing_arr) + ["<Enter new time>"],
    ).ask()

    if arr_choice == "<Enter new time>":
        arrival_time = questionary.text("Enter arrival (HH:MM):").ask()
    else:
        arrival_time = arr_choice

    # ================= VALIDATION =================
    from datetime import datetime

    try:
        datetime.strptime(travel_date, "%Y-%m-%d")
        datetime.strptime(departure_time, "%H:%M")
        datetime.strptime(arrival_time, "%H:%M")
    except Exception:
        console.print("[bold red]Invalid date/time format[/bold red]")
        return

    fare_input = questionary.text("Fare amount (₹):").ask()
    if not fare_input:
        console.print("[yellow]Operation cancelled[/yellow]")
        return

    try:
        fare = float(fare_input)
        if fare <= 0:
            raise ValueError
    except Exception:
        console.print("[bold red]Invalid fare. Enter a positive number[/bold red]")
        return

    try:
        sched_id = schedule_service.create_schedule(
            train_id,
            origin_id,
            dest_id,
            travel_date,
            departure_time,
            arrival_time,
            fare,
        )
        console.print(
            f"[bold green]Schedule created (id={sched_id}, Fare=₹{fare})[/bold green]"
        )

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
    journey_row_map = {}

    for r in rows:
        jid = r["id"]

        display = (
            f"{jid} | Train:{r['train_id']} | "
            f"{r['origin_station_id']}->{r['destination_station_id']} | "
            f"{r['travel_date']} {r['departure_time']}-{r['arrival_time']}"
        )

        journey_map[display] = jid
        journey_row_map[jid] = r

    choice = questionary.select(
        "Select journey to update:",
        choices=list(journey_map.keys()),
    ).ask()

    if not choice:
        return

    schedule_id = journey_map[choice]
    current = journey_row_map[schedule_id]

    # current values
    train_id = current["train_id"]
    origin_id = current["origin_station_id"]
    dest_id = current["destination_station_id"]
    travel_date = current["travel_date"]
    departure_time = current["departure_time"]
    arrival_time = current["arrival_time"]
    fare = current["fare"]

    console.print("\n[yellow]Press ENTER to keep existing value[/yellow]\n")

    # ================= STATIONS =================
    stations = station_service.list_stations()

    station_map = {}
    station_choices = []

    for s in stations:
        display = f"{s['id']} - {s['code']} - {s['name']}"
        station_map[display] = s["id"]
        station_choices.append(display)

    # ORIGIN
    origin_choice = questionary.select(
        f"Origin station [current: {origin_id}]",
        choices=["<keep current>"] + station_choices,
    ).ask()

    if origin_choice != "<keep current>":
        origin_id = station_map[origin_choice]

    # DESTINATION
    dest_choice = questionary.select(
        f"Destination station [current: {dest_id}]",
        choices=["<keep current>"] + station_choices,
    ).ask()

    if dest_choice != "<keep current>":
        dest_id = station_map[dest_choice]

    # ================= DATE/TIME =================
    new_date = questionary.text(f"Travel date (YYYY-MM-DD) [{travel_date}]:").ask()

    new_dep = questionary.text(f"Departure time (HH:MM) [{departure_time}]:").ask()

    new_arr = questionary.text(f"Arrival time (HH:MM) [{arrival_time}]:").ask()

    new_fare = questionary.text(f"Fare [{fare}]:").ask()

    # keep old if blank
    travel_date = new_date or travel_date
    departure_time = new_dep or departure_time
    arrival_time = new_arr or arrival_time
    fare = new_fare or fare

    # ================= VALIDATION =================
    from datetime import datetime

    try:
        datetime.strptime(travel_date, "%Y-%m-%d")
        datetime.strptime(departure_time, "%H:%M")
        datetime.strptime(arrival_time, "%H:%M")

        fare = float(fare)
        if fare < 0:
            raise ValueError
    except Exception:
        console.print("[bold red]Invalid date/time format[/bold red]")
        return

    # ================= UPDATE =================
    try:
        schedule_service.update_schedule(
            schedule_id,
            train_id,
            origin_id,
            dest_id,
            travel_date,
            departure_time,
            arrival_time,
            fare,
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


def admin_view_train_route_by_train() -> None:
    console.print("[cyan] View Train Route by Train[/cyan]")

    # ================= TRAIN SELECTION =================
    rows = train_service.list_trains()

    if not rows:
        console.print("[yellow]No trains available[/yellow]")
        return

    train_map = {}
    train_choices = []

    for r in rows:
        display = f"{r['id']} - {r['train_number']} - {r['train_name']}"
        train_map[display] = r["id"]
        train_choices.append(display)

    train_choice = questionary.select("Select Train:", choices=train_choices).ask()

    if not train_choice:
        return

    train_id = train_map[train_choice]

    try:
        from services import schedule as schedule_service
        from services import station as station_service

        schedules = schedule_service.get_schedules_by_train(train_id)

        if not schedules:
            console.print("[yellow]No journeys found for this train[/yellow]")
            return

        # ================= LOAD STATION NAMES =================
        stations = station_service.list_stations()
        station_lookup = {s["id"]: s["name"] for s in stations}

        # ================= GROUP ROUTES =================
        # key = (date, dep, arr)
        grouped = defaultdict(list)

        for r in schedules:
            key = (
                r["travel_date"],
                r["departure_time"],
                r["arrival_time"],
            )

            grouped[key].append(
                (
                    station_lookup.get(
                        r["origin_station_id"], str(r["origin_station_id"])
                    ),
                    station_lookup.get(
                        r["destination_station_id"], str(r["destination_station_id"])
                    ),
                )
            )

        # ================= DISPLAY =================
        console.print(f"\n[bold green]{train_choice}[/bold green]\n")

        for (date, dep, arr), routes in grouped.items():

            table = Table(show_header=True, header_style="bold magenta")

            table.title = f"Date: {date} | {dep} → {arr}"

            table.add_column("Route")

            # build route chain
            path = []
            for o, d in routes:
                if not path:
                    path.append(o)
                path.append(d)

            route_string = " → ".join(path)

            table.add_row(route_string)

            console.print(table)

    except Exception as e:
        console.print(f"[bold red] Error Viewing Train Routes: {e}[/bold red]")
