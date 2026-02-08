from __future__ import annotations

import questionary
from rich.console import Console
from rich.panel import Panel

from ui import messages


def register_customer(interactive: bool = True, username: str | None = None, email: str | None = None, password: str | None = None, full_name: str | None = None, dob: str | None = None, gender: str | None = None, mobile: str | None = None, aadhaar: str | None = None, nationality: str | None = None, address: str | None = None) -> dict:
    """Register a new customer (passenger).

    Mirrors the admin registration flow but uses `create_customer` service.
    """
    console = Console()
    console.print(Panel("Passenger Registration", style="bold blue", expand=False))

    if interactive:
        username = questionary.text("Username:").ask()
        full_name = questionary.text("Full name:").ask()
        dob = questionary.text("Date of birth (YYYY-MM-DD):").ask()
        gender = questionary.select("Gender:", choices=["male", "female", "other"]).ask()
        email = questionary.text("Email (optional if mobile provided):").ask()
        mobile = questionary.text("Mobile (optional if email provided):").ask()
        aadhaar = questionary.text("Aadhaar number (optional):").ask()
        nationality = questionary.text("Nationality (optional):").ask()
        address = questionary.text("Address (optional):").ask()
        password = questionary.password("Password (min 8 chars):").ask()

    try:
        from services.user import create_customer

        result = create_customer(
            username,
            email,
            password,
            full_name=full_name,
            dob=dob,
            gender=gender,
            mobile=mobile,
            aadhaar=aadhaar,
            nationality=nationality,
            address=address,
        )
        messages.show_success(f"Welcome, '{result['username']}'. Your account has been created.")
        return result
    except Exception as exc:
        messages.show_error(str(exc))
        raise



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
        choices = ["List passengers", "Add passenger", "Edit passenger", "Remove passenger", "Back"]
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
                        console.print(Panel(f"{idx}. {p.get('name','<no-name>')} — {p.get('dob','')}", title=str(idx)))

            elif action == "Add passenger":
                name = questionary.text("Name:").ask()
                dob = questionary.text("Date of birth (YYYY-MM-DD):").ask()
                gender = questionary.select("Gender:", choices=["male", "female", "other"]).ask()
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
                choices_idx = [f"{i+1}. {p.get('name','<no-name>')}" for i, p in enumerate(lst)]
                sel = questionary.select("Select passenger to edit:", choices=choices_idx).ask()
                if not sel:
                    continue
                idx = int(sel.split(".")[0]) - 1
                existing = lst[idx]
                name = questionary.text("Name:", default=existing.get("name","")).ask()
                dob = questionary.text("Date of birth (YYYY-MM-DD):", default=existing.get("dob","")).ask()
                gender = questionary.select("Gender:", choices=["male", "female", "other"], default=existing.get("gender","male")).ask()
                aadhaar = questionary.text("Aadhaar (optional):", default=existing.get("aadhaar","")).ask()
                mobile = questionary.text("Mobile (optional):", default=existing.get("mobile","")).ask()
                passenger = {"name": name, "dob": dob, "gender": gender, "aadhaar": aadhaar, "mobile": mobile}
                updated = user_service.update_passenger(user_id, idx, passenger)
                messages.show_success(f"Passenger updated. Total now: {len(updated)}")

            elif action == "Remove passenger":
                lst = user_service.list_passengers(user_id)
                if not lst:
                    messages.show_info("No passengers to remove.")
                    continue
                choices_idx = [f"{i+1}. {p.get('name','<no-name>')}" for i, p in enumerate(lst)]
                sel = questionary.select("Select passenger to remove:", choices=choices_idx).ask()
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
    messages.show_info("Booking UI not implemented yet.")


def booking_history_dashboard(username: str) -> None:
    console = Console()
    console.print(Panel(f"Booking History — {username}", style="bold magenta"))
    messages.show_info("Booking history not implemented yet.")


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