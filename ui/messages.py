from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console()


def show_success(message: str) -> None:
    console.print(Panel(message, title="Success", style="green"))


def show_error(message: str) -> None:
    console.print(Panel(message, title="Error", style="red"))


def show_info(message: str) -> None:
    console.print(Panel(message, title="Info", style="blue"))
