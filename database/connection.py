# database/connection.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "train_booking.db"

def get_connection():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # dictionary-like access
        return conn
    except sqlite3.Error as e:
        print("❌ Database connection failed:", e)
        raise

def close_connection(conn):
    if conn:
        conn.close()

