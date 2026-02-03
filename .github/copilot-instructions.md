## Purpose

This file gives short, actionable context for AI agents working on the TrainBookingSystem repo so they can be productive immediately.

## Big picture (what this repo is)

- A small CLI train booking application. Top-level modules:
  - `main.py` — program entry point (currently prints a greeting).
  - `cli/` — command-line handlers: `menu.py`, `admin.py`, `passenger.py` (add new commands here).
  - `services/` — business logic layer: `booking.py`, `train.py`, `user.py`.
  - `database/` — persistence: `connection.py`, `queries.py`, and `schema.sql` (DB schema lives here).
  - `ui/` — presentation helpers: `messages.py`, `table.py` (uses Rich for formatting).
  - `utils/` — shared helpers and validators.

The flow: `main.py` -> `cli` handlers -> `services` -> `database` (via `database/connection.py` + `database/queries.py`) -> `ui` for output formatting.

## Key conventions & patterns (repo-specific)

- CLI-first design: user interactions belong in `cli/*` and should be thin wrappers that parse input and call `services/*` functions.
- Business logic must live in `services/*` and be side-effect free where possible; they are the place to enforce rules (availability, seat counts, user lookup).
- Database access is centralized in `database/connection.py` and `database/queries.py`. Keep SQL or query text in `queries.py` and connection/session handling in `connection.py`.
- Presentation is handled by `ui/*` using Rich — prefer `ui/table.py` for tabular output and `ui/messages.py` for fixed user messages.
- Input validation helpers belong in `utils/validators.py` — use them early in the CLI layer.

## Dependencies & runtime

- Python >= 3.11 (see `pyproject.toml`).
- Direct dependencies listed in `pyproject.toml`: `questionary` (for interactive prompts) and `rich` (for terminal formatting).
- How to run locally (PowerShell):

```powershell
python -m pip install --upgrade pip
python -m pip install questionary rich
python main.py
```

If you add packaging/installation, update `pyproject.toml` appropriately.

## Typical dev workflows (what an agent should do)

- Adding a new CLI command: create/modify a function in `cli/menu.py` (or a specific handler file like `cli/admin.py`) and call a new `services` function. Keep I/O in `cli` and logic in `services`.
- Adding persistence: add SQL or query text in `database/queries.py`, then call it via a new helper in `database/connection.py` or from a `services` function.
- Presentation updates: change formatting in `ui/table.py` or `ui/messages.py` to keep formatting centralized.

## Examples (concrete pointers)

- To implement booking creation: add `create_booking()` to `services/booking.py`, expose a thin `cli` wrapper in `cli/passenger.py`, and store data via a `database/queries.py` INSERT.
- To add a new field to the database: update `schema.sql`, add queries in `database/queries.py`, and adapt `services/*` and `ui/*` to handle the new field.

## What not to change without checking

- Do not move user I/O into `services/*`. Keep `services` testable and free of prompting/print side-effects.
- Don't hardcode DB connection strings; follow the existing `database/connection.py` pattern (centralized connection management).

## Missing/unknowns (ask the maintainer)

- The repository lacks tests and most implementation files are currently empty; confirm desired DB engine (sqlite/postgres) and preferred test framework.
- Confirm whether packaging (editable install) or a virtualenv/poetry workflow is preferred.

---

If anything in these notes is unclear or if you'd like the instructions to include sample code snippets for a particular task (e.g., add booking flow or a unit test template), tell me which area to expand and I'll update this file.
