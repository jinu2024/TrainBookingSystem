from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ui import messages
from services import booking
from utils.__helper import ask_required, ask_with_validation
from utils.validators import (
    is_strong_password,
    is_valid_aadhaar,
    is_valid_date_of_birth,
    is_valid_email,
    is_valid_mobile_number,
)


def register_customer(
    interactive: bool = True,
    username: str | None = None,
    email: str | None = None,
    password: str | None = None,
    full_name: str | None = None,
    dob: str | None = None,
    gender: str | None = None,
    mobile: str | None = None,
    aadhaar: str | None = None,
    nationality: str | None = None,
    address: str | None = None,
) -> dict:
    console = Console()

    # console.print("[bold blue]Create new Account[/bold blue]\n")

    try:
        if interactive:
            username = ask_required("Username:")
            full_name = ask_required("Full name:")

            dob = ask_with_validation(
                "Date of birth (YYYY-MM-DD):",
                validator=is_valid_date_of_birth,
                error_msg="DOB must be YYYY-MM-DD and age ≥ 16",
            )
            if not dob:
                return

            gender = questionary.select(
                "Gender:",
                choices=["male", "female", "other"],
            ).ask()
            if gender is None:
                return

            email = ask_with_validation(
                "Email:",
                validator=is_valid_email,
                error_msg="Invalid email format",
            )
            if not email:
                return

            mobile = ask_with_validation(
                "Mobile (optional):",
                validator=is_valid_mobile_number,
                error_msg="Mobile must be 10 digits starting with 6,7,8,9",
            )
            if mobile is None:
                return

            aadhaar = ask_with_validation(
                "Aadhaar (optional):",
                validator=is_valid_aadhaar,
                error_msg="Aadhaar must contain only digits and 12 digits long",
            )
            if aadhaar is None:
                return

            nationality = ask_required("Nationality (optional):")
            address = ask_required("Address (optional):")

            messages.show_info(
                "Create a strong password mixed of special characters, numbers, upper and lower alphabets. 8-16 chars."
            )

            password = ask_with_validation(
                "Password:",
                validator=is_strong_password,
                error_msg="Password must be 8-16 chars with uppercase, lowercase, digit, and special character",
                password=True,
            )
            confirm_password = ask_with_validation(
                "Confirm password:",
                validator=is_strong_password,
                error_msg="Password must be 8-16 chars with uppercase, lowercase, digit, and special character",
                password=True,
            )

            if password != confirm_password:
                console.print("[bold red]Passwords do not match[/bold red]")
                return

        from services.user import create_customer

        print(f"aadhar :{aadhaar}")

        result = create_customer(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            dob=dob,
            gender=gender,
            mobile=mobile,
            aadhaar=aadhaar,
            nationality=nationality,
            address=address,
        )

        messages.show_success(f"Welcome, '{result['username']}'!")
        return result

    except KeyboardInterrupt:
        console.print("\n[bold red]Registration cancelled. Exiting...[/bold red]")
        raise SystemExit


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
        choice = questionary.select(
            "Passenger actions:",
            choices=[
                "Book Tickets",
                "View Booking History",
                "Edit Profile",
                "Manage passenger master list",
                "Help",
                "Close CLI",
                "Logout",
            ],
        ).ask()

        if choice == "Book Tickets":
            book_tickets_dashboard(username)
            continue

        if choice == "View Booking History":
            booking_history_dashboard(username)
            continue

        if choice == "Edit Profile":
            profile_dashboard(username)
            continue

        if choice == "Manage passenger master list":
            # find user id from username
            try:
                conn = None
                # we need to locate the user record to get id
                # reuse queries via connection module
                from database import connection, queries

                conn = connection.get_connection()
                user = queries.get_user_by_username(conn, username)
                if not user:
                    messages.show_error("User not found")
                else:
                    # open passenger manager
                    manage_passengers(user["id"])
            except Exception as exc:
                messages.show_error(f"Failed to manage passengers: {exc}")
            finally:
                try:
                    if conn:
                        connection.close_connection(conn)
                except Exception:
                    pass
            continue
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

        if choice == "Help":
            help_dashboard(username)
            continue

        if choice == "Close CLI":
            messages.show_info("Closing CLI — goodbye")
            raise SystemExit(0)


def manage_passengers(user_id: int) -> None:
    """Interactive passenger list manager for a given user id."""
    console = Console()
    console.print(Panel("Manage Passengers", style="bold green", expand=False))

    from services import user as user_service

    while True:
        choices = [
            "List passengers",
            "Add passenger",
            "Edit passenger",
            "Remove passenger",
            "Back",
        ]
        action = questionary.select("Passenger manager:", choices=choices).ask()
        if action == "Back" or not action:
            return

        try:
            if action == "List passengers":
                lst = user_service.list_passengers(user_id)
                if not lst:
                    messages.show_info("No passengers saved yet.")
                else:
                    for idx, p in enumerate(lst, start=1):
                        console.print(
                            Panel(
                                f"{idx}. {p.get('name','<no-name>')} — {p.get('dob','')}",
                                title=str(idx),
                            )
                        )

            elif action == "Add passenger":
                name = questionary.text("Name:").ask()
                dob = questionary.text("Date of birth (YYYY-MM-DD):").ask()
                gender = questionary.select(
                    "Gender:", choices=["male", "female", "other"]
                ).ask()
                aadhaar = questionary.text("Aadhaar (optional):").ask()
                mobile = questionary.text("Mobile (optional):").ask()
                passenger = {
                    "name": name,
                    "dob": dob,
                    "gender": gender,
                    "aadhaar": aadhaar,
                    "mobile": mobile,
                }
                updated = user_service.add_passenger(user_id, passenger)
                messages.show_success(f"Passenger added. Total now: {len(updated)}")

            elif action == "Edit passenger":
                lst = user_service.list_passengers(user_id)
                if not lst:
                    messages.show_info("No passengers to edit.")
                    continue
                choices_idx = [
                    f"{i+1}. {p.get('name','<no-name>')}" for i, p in enumerate(lst)
                ]
                sel = questionary.select(
                    "Select passenger to edit:", choices=choices_idx
                ).ask()
                if not sel:
                    continue
                idx = int(sel.split(".")[0]) - 1
                existing = lst[idx]
                name = questionary.text("Name:", default=existing.get("name", "")).ask()
                dob = questionary.text(
                    "Date of birth (YYYY-MM-DD):", default=existing.get("dob", "")
                ).ask()
                gender = questionary.select(
                    "Gender:",
                    choices=["male", "female", "other"],
                    default=existing.get("gender", "male"),
                ).ask()
                aadhaar = questionary.text(
                    "Aadhaar (optional):", default=existing.get("aadhaar", "")
                ).ask()
                mobile = questionary.text(
                    "Mobile (optional):", default=existing.get("mobile", "")
                ).ask()
                passenger = {
                    "name": name,
                    "dob": dob,
                    "gender": gender,
                    "aadhaar": aadhaar,
                    "mobile": mobile,
                }
                updated = user_service.update_passenger(user_id, idx, passenger)
                messages.show_success(f"Passenger updated. Total now: {len(updated)}")

            elif action == "Remove passenger":
                lst = user_service.list_passengers(user_id)
                if not lst:
                    messages.show_info("No passengers to remove.")
                    continue
                choices_idx = [
                    f"{i+1}. {p.get('name','<no-name>')}" for i, p in enumerate(lst)
                ]
                sel = questionary.select(
                    "Select passenger to remove:", choices=choices_idx
                ).ask()
                if not sel:
                    continue
                idx = int(sel.split(".")[0]) - 1
                updated = user_service.remove_passenger(user_id, idx)
                messages.show_success(f"Passenger removed. Total now: {len(updated)}")

        except IndexError as ie:
            messages.show_error(str(ie))
        except Exception as exc:
            messages.show_error(f"Error: {exc}")


def book_tickets_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel(f"Book Tickets — {username}", style="bold magenta"))

    try:
        from database import connection, queries
        from services.booking import book_ticket
        from services.payments import process_payment
        from utils.validators import is_valid_schedule_date

        conn = connection.get_connection()

        # -----------------------------
        # SELECT ORIGIN & DESTINATION
        # -----------------------------
        stations = queries.get_all_stations(conn)
        if not stations:
            messages.show_error("No stations available")
            return

        station_choices = [f"{s['id']} - {s['name']} ({s['city']})" for s in stations]

        origin = questionary.select("Select origin station:", choices=station_choices).ask()
        if not origin:
            return

        destination = questionary.select("Select destination station:", choices=station_choices).ask()
        if not destination:
            return

        origin_id = int(origin.split(" - ")[0])
        destination_id = int(destination.split(" - ")[0])

        if origin_id == destination_id:
            messages.show_error("Origin and destination cannot be same")
            return

        # -----------------------------
        # VALIDATED DEPARTURE DATE
        # -----------------------------
        while True:
            travel_date = questionary.text("Departure date (YYYY-MM-DD):").ask()
            if not travel_date:
                return

            if not is_valid_schedule_date(travel_date):
                messages.show_error("Invalid date. Must not be past and within 1 year.")
                continue
            break

        # -----------------------------
        # FIND MATCHING SCHEDULES
        # -----------------------------
        schedules = queries.find_schedules(conn, origin_id, destination_id, travel_date)

        if not schedules:
            messages.show_info("No trains available for this route and date.")
            return

        train_choices = {}
        for s in schedules:
            label = (
                f"{s['train_number']} ({s['train_name']}) | "
                f"{s['departure_date']} {s['departure_time']} → "
                f"{s['arrival_date']} {s['arrival_time']} | "
                f"Fare ₹{s['fare']}"
            )
            train_choices[label] = s

        selected_label = questionary.select(
            "Select train:", choices=list(train_choices.keys())
        ).ask()

        if not selected_label:
            return

        selected_schedule = train_choices[selected_label]

        train_id = selected_schedule["train_id"]
        fare = selected_schedule["fare"]

        # -----------------------------
        # CONFIRM JOURNEY DETAILS
        # -----------------------------
        console.print(
            Panel(
                f"""
Train        : {selected_schedule['train_number']} - {selected_schedule['train_name']}
Route        : {origin.split('-')[1].strip()} → {destination.split('-')[1].strip()}
Departure    : {selected_schedule['departure_date']} {selected_schedule['departure_time']}
Arrival      : {selected_schedule['arrival_date']} {selected_schedule['arrival_time']}
Fare         : ₹{fare}
                """,
                title="Confirm Journey",
                style="cyan",
            )
        )

        if not questionary.confirm("Proceed to payment?").ask():
            return

        # ====================================================
        # 💳 DUMMY PAYMENT VALIDATION SECTION (NEW)
        # ====================================================

        DUMMY_CARD = "1111222233334444"
        DUMMY_EXPIRY = "12/30"
        DUMMY_CVV = "123"
        DUMMY_OTP = "0000"

        console.print(
            Panel(
                """
[bold yellow]Demo Card Details:[/bold yellow]

Card Number : 1111222233334444
Expiry      : 12/30
CVV         : 123
OTP         : 0000
                """,
                style="yellow",
            )
        )

        while True:

            card = questionary.text("Card Number:").ask()
            expiry = questionary.text("Expiry (MM/YY):").ask()
            cvv = questionary.password("CVV:").ask()
            otp = questionary.text("Enter OTP:").ask()

            if (
                card == DUMMY_CARD
                and expiry == DUMMY_EXPIRY
                and cvv == DUMMY_CVV
                and otp == DUMMY_OTP
            ):
                messages.show_success("Payment validated successfully.")
                break
            else:
                messages.show_error("Invalid card details. Try again.")

        # -----------------------------
        # PROCESS PAYMENT
        # -----------------------------
        payment = process_payment(amount=fare, method="card")

        booking = book_ticket(
            username=username,
            train_id=train_id,
            origin_station_id=origin_id,
            destination_station_id=destination_id,
            travel_date=travel_date,
            fare=fare,
            payment=payment,
        )

        console.print(
            Panel(
                f"""
✅ Booking Confirmed!

Booking Code : {booking['booking_code']}
Train        : {booking['train_number']} - {booking['train_name']}
Departure    : {selected_schedule['departure_date']} {selected_schedule['departure_time']}
Arrival      : {selected_schedule['arrival_date']} {selected_schedule['arrival_time']}
Amount Paid  : ₹{fare}

🎟️ Have a safe journey!
                """,
                style="bold green",
            )
        )

    except Exception as exc:
        messages.show_error(str(exc))

    finally:
        try:
            connection.close_connection(conn)
        except Exception:
            pass


def booking_history_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel(f"Booking History — {username}", style="bold magenta"))

    try:
        bookings = booking.get_booking_history(username)

        if not bookings:
            messages.show_info("No bookings found.")
            return

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Booking Code")
        table.add_column("Train")
        table.add_column("Route")
        table.add_column("Date")
        table.add_column("Fare", justify="right")
        table.add_column("Booking Status")
        table.add_column("Payment Status")
        table.add_column("Txn ID")
        table.add_column("Action")

        cancellable_bookings = {}

        for b in bookings:

            booking_status = (
                "[green]CONFIRMED[/green]"
                if b["booking_status"] == "confirmed"
                else "[red]CANCELLED[/red]"
            )

            if b["payment_status"] == "success":
                payment_status = "[green]SUCCESS[/green]"
            elif b["payment_status"] == "refunded":
                payment_status = "[yellow]REFUNDED[/yellow]"
            else:
                payment_status = "-"

            # Action column
            if b["booking_status"] == "confirmed":
                action = "[red]Delete[/red]"
                cancellable_bookings[b["booking_code"]] = b
            else:
                action = "-"

            table.add_row(
                b["booking_code"],
                f'{b["train_number"]} {b["train_name"]}',
                f'{b["origin_station"]} → {b["destination_station"]}',
                b["travel_date"],
                f'₹{b["fare"]}',
                booking_status,
                payment_status,
                b["transaction_id"] or "-",
                action,
            )

        console.print(table)

        # ---------------------------------
        # Cancel Flow
        # ---------------------------------
        if cancellable_bookings:

            selected = questionary.select(
                "Select booking to delete (or Back):",
                choices=list(cancellable_bookings.keys()) + ["Back"],
            ).ask()

            if not selected or selected == "Back":
                return

            if questionary.confirm(
                f"Are you sure you want to delete booking {selected}?"
            ).ask():

                from services.booking import cancel_booking_by_code

                result = cancel_booking_by_code(selected)

                console.print(
                    Panel(
                        f"""
                            [bold green]Booking Cancelled Successfully[/bold green]

                            Original Fare : ₹{result['original_amount']}
                            Refund Amount : ₹{result['refund_amount']}

                            Deduction     : ₹{result['deduction']}

                            Hours before departure: {result['hours_remaining']} hrs
                                                    """,
                        style="green",
                    )
                )

    except ValueError as e:
        messages.show_warning(str(e))

    except Exception as e:
        messages.show_error(str(e))


def profile_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel(f"Profile — {username}", style="bold magenta"))
    messages.show_info("Profile editing not implemented yet.")


def help_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel("Passenger Help", style="bold yellow"))
    messages.show_info("Help is not available yet.")


if __name__ == "__main__":
    # quick manual test
    passenger_dashboard("demo_passenger")
