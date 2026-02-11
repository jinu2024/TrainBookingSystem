import questionary
from rich.console import Console


import questionary
from rich.console import Console

console = Console()


def ask_required(
    prompt: str,
    password: bool = False,
    attempts: int = 3,
    validator=None,
    error_msg: str = "Invalid input. Try again.",
):
    """
    Safe questionary input with:
    - Required value
    - Retry attempts
    - Optional validator function
    - Ctrl+C safe exit
    """

    for _ in range(attempts):
        try:
            # Ask input
            value = (
                questionary.password(prompt).ask()
                if password
                else questionary.text(prompt).ask()
            )

            if value is None:  # Ctrl+C or ESC
                raise KeyboardInterrupt

            value = value.strip()

            # Required check
            if not value:
                console.print("[yellow]Input cannot be empty[/yellow]")
                continue

            # Custom validator
            if validator and not validator(value):
                console.print(f"[red]{error_msg}[/red]")
                continue

            return value

        except KeyboardInterrupt:
            console.print("\n[bold red]Operation cancelled. Exiting...[/bold red]")
            raise SystemExit

    console.print("[bold red]Too many failed attempts. Exiting...[/bold red]")
    raise SystemExit


def ask_with_validation(
    prompt: str,
    validator=lambda x: True,
    error_msg: str = "Invalid input",
    password: bool = False,
    attempts: int = 3,
):
    """
    Ask input with validation + retry.
    Returns valid value or exits after max attempts.
    """
    console = Console()
    for i in range(attempts):
        value = ask_required(prompt, password=password)

        # allow empty (for optional fields)
        if value == "" or value is None:
            return value

        if validator(value):
            return value

        remaining = attempts - i - 1

        if remaining > 0:
            console.print(
                f"[bold red]{error_msg}[/bold red] ({remaining} attempts left)"
            )
        else:
            console.print(
                "[bold red]Too many invalid attempts. Registration cancelled.[/bold red]"
            )
            return None
