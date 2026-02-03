from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterator

from . import queries

DB_PATH = Path(__file__).parent.parent / "train_booking.db"


def get_connection() -> sqlite3.Connection:
    """Return a sqlite3 connection and ensure schema exists.

    The DB file lives at the repository root as `train_booking.db`.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # ensure tables
    queries.create_tables(conn)
    return conn


def close_connection(conn: sqlite3.Connection) -> None:
    try:
        conn.commit()
    finally:
        conn.close()
