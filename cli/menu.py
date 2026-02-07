from __future__ import annotations

import sys
import questionary
from rich.panel import Panel
from rich.console import Console

from ui import messages
from cli import admin as admin_cli
from cli import passenger as passenger_cli
from services import user as user_service

console = Console()


def main_menu() -> None:
	console.print(Panel("Train Booking System", style="bold green", expand=False))

	while True:
		choice = questionary.select(
			"Main Menu",
			choices=["Sign up", "Sign in", "About", "Exit"],
		).ask()

		if choice == "Sign up":
			signup_menu()
		elif choice == "Sign in":
			try:
				# single sign-in page for both admin and passenger
				identifier = questionary.text("Username or Email:").ask()
				password = questionary.password("Password:").ask()
				user = user_service.authenticate_user(identifier, password)
				role = user.get("role")
				if role == "admin":
					admin_cli.admin_dashboard(user.get("username"))
				else:
					# create a session for customers (24h TTL) and pass token to dashboard
					from services import session as session_service
					token = session_service.create_session_for_user(user.get("id"))
					passenger_cli.passenger_dashboard(user.get("username"), session_token=token)
			except Exception as exc:
				messages.show_error(str(exc))
		elif choice == "About":
			messages.show_info("TrainBookingSystem — CLI demo. See README.md for details.")
		elif choice == "Exit":
			console.print("Goodbye.")
			sys.exit(0)


def signup_menu() -> None:
	choice = questionary.select("Sign up as:", choices=["Admin", "Passenger", "Back"]).ask()
	if choice == "Admin":
		try:
			admin_cli.register_admin()
		except Exception:
			# register_admin already shows errors via ui.messages
			pass
	elif choice == "Passenger":
		try:
			passenger_cli.register_customer()
		except Exception:
			# register_customer already shows errors via ui.messages
			pass
	elif choice == "Back":
		return


if __name__ == "__main__":
	main_menu()
