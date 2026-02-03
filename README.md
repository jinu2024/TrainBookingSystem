# TrainBookingSystem

Minimal CLI train booking demo application.

## Requirements

- Python 3.11+
- Optional: a virtual environment (recommended)

Dependencies are declared in `pyproject.toml`. The runtime dependencies are:

- `questionary` — interactive CLI prompts
- `rich` — terminal formatting and panels

Dev/test dependencies (optional) are declared under `[project.optional-dependencies]` in `pyproject.toml` (e.g. `pytest`).

## Quick start (PowerShell)

1. Create and activate a venv (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install runtime dependencies:

```powershell
uv sync
```

3. Run the interactive CLI:

```powershell
python main.py
```

The main menu supports: Sign up, Sign in, About, Exit. Choose Sign up → Admin to register a new admin.

4. Run the demo (non-interactive) to create a sample admin:

```powershell
python main.py --demo
```

Note: the demo and runtime use a local SQLite database file `train_booking.db` created at the project root. Delete that file to reset data between runs.

## Running tests

Install pytest (into your venv) and run the tests:

```powershell
python -m pip install pytest
python -m pytest -q
```

## Project structure (high level)

- `main.py` — entry point and CLI launcher
- `cli/` — command handlers (menu, admin, passenger)
- `services/` — business logic (user, booking, train)
- `database/` — connection and SQL queries (`train_booking.db` sqlite file)
- `ui/` — presentation helpers using Rich
- `utils/` — small validators and helpers
- `tests/` — pytest unit tests

