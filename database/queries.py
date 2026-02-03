"""SQL queries and helpers for TrainBookingSystem.

Keep SQL centralized here. This module is intentionally small and focused on
the `users` table for the admin registration flow.
"""
from __future__ import annotations

import sqlite3

CREATE_TABLE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'passenger',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_USER = """
INSERT INTO users (username, email, password_hash, role)
VALUES (?, ?, ?, ?)
"""

SELECT_USER_BY_USERNAME = "SELECT * FROM users WHERE username = ?"
SELECT_USER_BY_EMAIL = "SELECT * FROM users WHERE email = ?"


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.executescript(CREATE_TABLE_USERS)
    conn.commit()


def create_user(conn: sqlite3.Connection, username: str, email: str, password_hash: str, role: str = "passenger") -> int:
    cur = conn.cursor()
    cur.execute(INSERT_USER, (username, email, password_hash, role))
    conn.commit()
    return cur.lastrowid


def get_user_by_username(conn: sqlite3.Connection, username: str):
    cur = conn.cursor()
    cur.execute(SELECT_USER_BY_USERNAME, (username,))
    return cur.fetchone()


def get_user_by_email(conn: sqlite3.Connection, email: str):
    cur = conn.cursor()
    cur.execute(SELECT_USER_BY_EMAIL, (email,))
    return cur.fetchone()
