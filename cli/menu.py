from __future__ import annotations

import sys
import questionary
from rich.panel import Panel
from rich.console import Console

from ui import messages
from cli import admin as admin_cli

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
			messages.show_info("Sign in is not implemented yet.")
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
		messages.show_info("Passenger sign up not implemented yet.")
	elif choice == "Back":
		return


if __name__ == "__main__":
	main_menu()
