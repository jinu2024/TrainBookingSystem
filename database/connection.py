# database/connection.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "train_booking.db"


def get_connection():
    """Return a sqlite3 connection and ensure schema is applied.

    The schema is loaded from the repository-level `schema.sql`.
    """
    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # dictionary-like access

        # ensure schema exists (idempotent)
        schema_path = Path(__file__).resolve().parents[1] / "schema.sql"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

        return conn
    except sqlite3.Error as e:
        print("❌ Database connection failed:", e)
        raise


def close_connection(conn):
    if conn:
        conn.close()

