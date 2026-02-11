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
                "Download Ticket (PDF)",
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

        if choice == "Download Ticket (PDF)":
            try:
                download_ticket_dashboard(username)
            except Exception as exc:
                messages.show_error(f"Failed to download ticket: {exc}")
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


def profile_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel(f"Profile — {username}", style="bold magenta"))

    try:
        from database import connection, queries
        from utils.validators import (
            is_valid_email,
            is_valid_mobile_number,
            is_valid_aadhaar,
        )

        conn = connection.get_connection()
        user = queries.get_user_by_username(conn, username)

        if not user:
            messages.show_error("User not found.")
            return

        user = dict(user)

        while True:
            choice = questionary.select(
                "Profile Options:",
                choices=[
                    "View Profile",
                    "Edit Email",
                    "Edit Mobile",
                    "Edit Address",
                    "Edit Aadhaar",
                    "Back",
                ],
            ).ask()

            if choice == "Back":
                return

            # --------------------------------------------------
            # VIEW PROFILE
            # --------------------------------------------------
            if choice == "View Profile":
                console.print(
                    Panel(
                        f"""
Username     : {user['username']}
Full Name    : {user.get('full_name', 'N/A')}
Email        : {user.get('email', 'N/A')}
Mobile       : {user.get('mobile', 'N/A')}
DOB          : {user.get('dob', 'N/A')}
Gender       : {user.get('gender', 'N/A')}
Nationality  : {user.get('nationality', 'N/A')}
Address      : {user.get('address', 'N/A')}
Aadhaar      : {user.get('aadhaar', 'N/A')}
                        """,
                        style="cyan",
                    )
                )

            # --------------------------------------------------
            # EDIT EMAIL
            # --------------------------------------------------
            elif choice == "Edit Email":

                new_email = questionary.text("Enter new email:").ask()
                confirm_email = questionary.text("Re-enter new email:").ask()

                if new_email != confirm_email:
                    messages.show_error("Emails do not match.")
                    continue

                if not is_valid_email(new_email):
                    messages.show_error("Invalid email format.")
                    continue

                existing = queries.get_user_by_email(conn, new_email)
                if existing and existing["username"] != username:
                    messages.show_error("Email already registered.")
                    continue

                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET email = ? WHERE username = ?",
                    (new_email.strip(), username),
                )
                conn.commit()

                messages.show_success("Email updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

            # --------------------------------------------------
            # EDIT MOBILE
            # --------------------------------------------------
            elif choice == "Edit Mobile":

                new_mobile = questionary.text("Enter new mobile number:").ask()
                confirm_mobile = questionary.text("Re-enter new mobile number:").ask()

                if new_mobile != confirm_mobile:
                    messages.show_error("Mobile numbers do not match.")
                    continue

                if not is_valid_mobile_number(new_mobile):
                    messages.show_error(
                        "Mobile must be 10 digits starting with 6,7,8,9."
                    )
                    continue

                existing = queries.get_user_by_mobile(conn, new_mobile)
                if existing and existing["username"] != username:
                    messages.show_error("Mobile already registered.")
                    continue

                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET mobile = ? WHERE username = ?",
                    (new_mobile.strip(), username),
                )
                conn.commit()

                messages.show_success("Mobile updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

            # --------------------------------------------------
            # EDIT ADDRESS
            # --------------------------------------------------
            elif choice == "Edit Address":

                new_address = questionary.text("Enter new address:").ask()
                confirm_address = questionary.text("Re-enter new address:").ask()

                if new_address != confirm_address:
                    messages.show_error("Addresses do not match.")
                    continue

                if not new_address or len(new_address.strip()) < 5:
                    messages.show_error("Address must be at least 5 characters.")
                    continue

                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET address = ? WHERE username = ?",
                    (new_address.strip(), username),
                )
                conn.commit()

                messages.show_success("Address updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

            # --------------------------------------------------
            # EDIT AADHAAR
            # --------------------------------------------------
            elif choice == "Edit Aadhaar":

                new_aadhaar = questionary.text("Enter new Aadhaar number:").ask()
                confirm_aadhaar = questionary.text("Re-enter new Aadhaar number:").ask()

                if new_aadhaar != confirm_aadhaar:
                    messages.show_error("Aadhaar numbers do not match.")
                    continue

                if not is_valid_aadhaar(new_aadhaar):
                    messages.show_error("Aadhaar must be exactly 12 digits.")
                    continue

                # Duplicate check
                cur = conn.cursor()
                cur.execute(
                    "SELECT * FROM users WHERE aadhaar = ?",
                    (new_aadhaar,),
                )
                existing = cur.fetchone()

                if existing and existing["username"] != username:
                    messages.show_error("Aadhaar already registered.")
                    continue

                cur.execute(
                    "UPDATE users SET aadhaar = ? WHERE username = ?",
                    (new_aadhaar.strip(), username),
                )
                conn.commit()

                messages.show_success("Aadhaar updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

    except Exception as e:
        messages.show_error(str(e))

    finally:
        try:
            connection.close_connection(conn)
        except Exception:
            pass


def profile_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel(f"Profile — {username}", style="bold magenta"))

    try:
        from database import connection, queries
        from utils.validators import (
            is_valid_email,
            is_valid_mobile_number,
            is_valid_aadhaar,
        )

        conn = connection.get_connection()
        user_row = queries.get_user_by_username(conn, username)

        if not user_row:
            messages.show_error("User not found.")
            return

        user = dict(user_row)  # ✅ Convert sqlite row → dict

        while True:

            choice = questionary.select(
                "Profile Options:",
                choices=[
                    "View Profile",
                    "Edit Email",
                    "Edit Mobile",
                    "Edit Address",
                    "Edit Aadhaar",
                    "Back",
                ],
            ).ask()

            if choice == "Back":
                break

            # --------------------------------------------------
            # VIEW PROFILE
            # --------------------------------------------------
            if choice == "View Profile":
                console.print(
                    Panel(
                        f"""
Username     : {user.get('username')}
Full Name    : {user.get('full_name') or 'N/A'}
Email        : {user.get('email') or 'N/A'}
Mobile       : {user.get('mobile') or 'N/A'}
DOB          : {user.get('dob') or 'N/A'}
Gender       : {user.get('gender') or 'N/A'}
Nationality  : {user.get('nationality') or 'N/A'}
Address      : {user.get('address') or 'N/A'}
Aadhaar      : {user.get('aadhaar') or 'N/A'}
                        """,
                        style="cyan",
                    )
                )

            # --------------------------------------------------
            # EDIT EMAIL
            # --------------------------------------------------
            elif choice == "Edit Email":

                new_email = questionary.text("Enter new email:").ask()
                confirm_email = questionary.text("Re-enter new email:").ask()

                if new_email != confirm_email:
                    messages.show_error("Emails do not match.")
                    continue

                if not is_valid_email(new_email):
                    messages.show_error("Invalid email format.")
                    continue

                existing = queries.get_user_by_email(conn, new_email)
                if existing and dict(existing)["username"] != username:
                    messages.show_error("Email already registered.")
                    continue

                conn.execute(
                    "UPDATE users SET email = ? WHERE username = ?",
                    (new_email.strip(), username),
                )
                conn.commit()

                messages.show_success("Email updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

            # --------------------------------------------------
            # EDIT MOBILE
            # --------------------------------------------------
            elif choice == "Edit Mobile":

                new_mobile = questionary.text("Enter new mobile number:").ask()
                confirm_mobile = questionary.text("Re-enter new mobile number:").ask()

                if new_mobile != confirm_mobile:
                    messages.show_error("Mobile numbers do not match.")
                    continue

                if not is_valid_mobile_number(new_mobile):
                    messages.show_error(
                        "Mobile must be 10 digits starting with 6,7,8,9."
                    )
                    continue

                existing = queries.get_user_by_mobile(conn, new_mobile)
                if existing and dict(existing)["username"] != username:
                    messages.show_error("Mobile already registered.")
                    continue

                conn.execute(
                    "UPDATE users SET mobile = ? WHERE username = ?",
                    (new_mobile.strip(), username),
                )
                conn.commit()

                messages.show_success("Mobile updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

            # --------------------------------------------------
            # EDIT ADDRESS
            # --------------------------------------------------
            elif choice == "Edit Address":

                new_address = questionary.text("Enter new address:").ask()
                confirm_address = questionary.text("Re-enter new address:").ask()

                if new_address != confirm_address:
                    messages.show_error("Addresses do not match.")
                    continue

                if not new_address or len(new_address.strip()) < 5:
                    messages.show_error("Address must be at least 5 characters.")
                    continue

                conn.execute(
                    "UPDATE users SET address = ? WHERE username = ?",
                    (new_address.strip(), username),
                )
                conn.commit()

                messages.show_success("Address updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

            # --------------------------------------------------
            # EDIT AADHAAR
            # --------------------------------------------------
            elif choice == "Edit Aadhaar":

                new_aadhaar = questionary.text("Enter new Aadhaar number:").ask()
                confirm_aadhaar = questionary.text("Re-enter new Aadhaar number:").ask()

                if new_aadhaar != confirm_aadhaar:
                    messages.show_error("Aadhaar numbers do not match.")
                    continue

                if not is_valid_aadhaar(new_aadhaar):
                    messages.show_error("Aadhaar must be exactly 12 digits.")
                    continue

                existing = conn.execute(
                    "SELECT * FROM users WHERE aadhaar = ?",
                    (new_aadhaar,),
                ).fetchone()

                if existing and dict(existing)["username"] != username:
                    messages.show_error("Aadhaar already registered.")
                    continue

                conn.execute(
                    "UPDATE users SET aadhaar = ? WHERE username = ?",
                    (new_aadhaar.strip(), username),
                )
                conn.commit()

                messages.show_success("Aadhaar updated successfully.")
                user = dict(queries.get_user_by_username(conn, username))

    except Exception as e:
        messages.show_error(str(e))

    finally:
        try:
            connection.close_connection(conn)
        except Exception:
            pass


def help_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel("Passenger Help Center", style="bold yellow"))

    help_text = """
        📌 BOOKING TICKETS
        - Select origin and destination stations.
        - Choose valid departure date.
        - Complete payment using card details.

        📌 CANCELLATION POLICY
        - Cancel ≥ 6 hours before departure → Full refund.
        - Cancel < 6 hours before departure → 10% deduction.
        - Cancellation after departure is not recommended.

        📌 DOWNLOAD TICKET
        - Only confirmed bookings can be downloaded.
        - Ticket is saved in the 'tickets' folder.
        - Ticket opens automatically after generation.

        📌 PROFILE MANAGEMENT
        - You can update email, mobile, and address.
        - Ensure correct information for ticket accuracy.

        📌 SUPPORT
        For assistance, contact:
        support_champion@trainbookingsystem.com

        Thank you for using Train Booking System!
            """

    console.print(Panel(help_text, style="yellow"))


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


def download_ticket_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel(f"Download Ticket — {username}", style="bold green"))

    try:
        from services.booking import get_booking_history
        from services.ticket_pdf import generate_ticket_pdf
        import os
        import platform
        import subprocess

        # -------------------------------------
        # Fetch booking history
        # -------------------------------------
        bookings = get_booking_history(username)

        if not bookings:
            messages.show_info("No bookings available.")
            return

        # Only confirmed bookings allowed
        confirmed_bookings = [
            b for b in bookings if b["booking_status"] == "confirmed"
        ]

        if not confirmed_bookings:
            messages.show_info("No confirmed bookings available for download.")
            return

        # -------------------------------------
        # Build selection list
        # -------------------------------------
        booking_choices = {
            f"{b['booking_code']} | "
            f"{b['train_number']} {b['train_name']} | "
            f"{b['origin_station']} → {b['destination_station']} | "
            f"{b['travel_date']}": b
            for b in confirmed_bookings
        }

        selected_label = questionary.select(
            "Select booking to download ticket:",
            choices=list(booking_choices.keys()) + ["Back"],
        ).ask()

        if not selected_label or selected_label == "Back":
            return

        # Convert sqlite3.Row → dict
        selected_booking = dict(booking_choices[selected_label])

        # -------------------------------------
        # Create tickets directory
        # -------------------------------------
        tickets_dir = "tickets"
        os.makedirs(tickets_dir, exist_ok=True)

        file_name = f"ticket_{selected_booking['booking_code']}.pdf"
        file_path = os.path.join(tickets_dir, file_name)

        # -------------------------------------
        # Generate PDF
        # -------------------------------------
        generate_ticket_pdf(selected_booking, file_path)

        # -------------------------------------
        # Auto-open PDF
        # -------------------------------------
        try:
            system_name = platform.system()

            if system_name == "Windows":
                os.startfile(file_path)

            elif system_name == "Darwin":  # macOS
                subprocess.call(["open", file_path])

            elif system_name == "Linux":
                subprocess.call(["xdg-open", file_path])

            console.print(
                Panel(
                    f"""
[bold green]Ticket Generated Successfully![/bold green]

File Name : {file_name}
Saved In  : {tickets_dir}/

Opening ticket automatically...
                    """,
                    style="green",
                )
            )

        except Exception:
            console.print(
                Panel(
                    f"""
[bold yellow]Ticket Generated Successfully![/bold yellow]

File Name : {file_name}
Saved In  : {tickets_dir}/

Could not auto-open the file.
Please open it manually from the tickets folder.
                    """,
                    style="yellow",
                )
            )

    except Exception as e:
        messages.show_error(str(e))


if __name__ == "__main__":
    # quick manual test
    passenger_dashboard("demo_passenger")
