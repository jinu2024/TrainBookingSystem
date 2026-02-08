def main(argv=None):
    """Start the TrainBookingSystem CLI.

    If `--demo` is passed in argv, run a non-interactive demo that creates a
    sample admin and exits. Otherwise start the interactive main menu.
    """
    import sys

    argv = argv if argv is not None else sys.argv[1:]

    if "--demo" in argv:
        # non-interactive smoke/demonstration mode
        from services.user import create_admin

        try:
            admin = create_admin("demo_admin", "demo@example.com", "demopassword")
            print(f"Demo admin created: {admin}")
        except Exception as exc:
            print("Demo failed:", exc)
        return

    # interactive mode: launch main menu
    try:
        from rich.console import Console
        from rich.panel import Panel

        console = Console()
        console.print(Panel("Launching Train Booking System interactive CLI", style="bold green"))

        # If stdin is not a TTY (non-interactive environment), show a simple
        # textual fallback so the main menu is still visible in logs.
        import sys

        if not sys.stdin.isatty():
            console.print("Non-interactive environment detected.\nAvailable actions: Sign up, Sign in, About, Exit")
            return

        from cli.menu import main_menu
        from database.queries import init_db
        
        init_db()
        main_menu()
    except Exception as exc:
        print("Error launching CLI:", exc)


if __name__ == "__main__":
    main()
