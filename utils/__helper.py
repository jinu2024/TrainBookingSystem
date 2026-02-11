import questionary
from rich.console import Console


def ask_required(prompt: str, password: bool = False):
    """Safe questionary input that exits immediately on Ctrl+C"""
    try:
        if password:
            value = questionary.password(prompt).ask()
        else:
            value = questionary.text(prompt).ask()

        if value is None:  # Ctrl+C or ESC
            raise KeyboardInterrupt

        return value

    except KeyboardInterrupt:
        console = Console()
        console.print("\n[bold red]Registration cancelled. Exiting...[/bold red]")
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
