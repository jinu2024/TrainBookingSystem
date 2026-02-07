import sys
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

import questionary

from database import connection, queries
from services import user as user_service
from services import session as session_service
from cli import admin as admin_cli
from cli import passenger as passenger_cli
from cli import menu as menu_cli


def setup_temp_db(tmp_path):
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    conn = connection.get_connection()
    conn.close()
    return db_file


class DummyPrompt:
    def __init__(self, value):
        self._value = value

    def ask(self):
        return self._value


def make_sequenced_prompts(seq):
    """Return fake select/text/password functions that consume values from seq list."""

    def fake_select(prompt, choices=None):
        return DummyPrompt(seq.pop(0))

    def fake_text(prompt):
        return DummyPrompt(seq.pop(0))

    def fake_password(prompt):
        return DummyPrompt(seq.pop(0))

    return fake_select, fake_text, fake_password


def test_main_menu_admin_flow(tmp_path, monkeypatch):
    """Integration: menu -> admin register -> admin login -> admin dashboard -> logout -> exit"""
    setup_temp_db(tmp_path)

    username = "int_admin"
    email = "int_admin@example.com"
    password = "strongpass"

    # sequence of responses for the interactive prompts
    # Main Menu: Sign up
    # Sign up as: Admin
    # Username, Email, Password for registration
    # Main Menu: Sign in
    # Username or Email, Password for sign in
    # Admin dashboard: Logout
    # Main Menu: Exit
    seq = [
        "Sign up",
        "Admin",
        username,
        email,
        password,
        "Sign in",
        username,
        password,
        "Logout",
        "Exit",
    ]

    fake_select, fake_text, fake_password = make_sequenced_prompts(seq)

    monkeypatch.setattr(questionary, "select", fake_select)
    monkeypatch.setattr(questionary, "text", fake_text)
    monkeypatch.setattr(questionary, "password", fake_password)

    # prevent real sys.exit from stopping the test
    with pytest.raises(SystemExit):
        menu_cli.main_menu()

    # verify admin exists
    conn = sqlite3.connect(connection.DB_PATH)
    conn.row_factory = sqlite3.Row
    row = queries.get_user_by_username(conn, username)
    assert row is not None and row["role"] == "admin"
    conn.close()


def test_customer_session_expiry_across_rerun(tmp_path, monkeypatch):
    """Create customer, sign in (create session), then simulate program rerun with expired session leading to auto logout."""
    setup_temp_db(tmp_path)

    # create customer
    res = user_service.create_customer(
        "int_cust",
        "int_cust@example.com",
        "custpass123",
        full_name="Integration Cust",
        dob="1992-02-02",
        gender="other",
    )
    # create session
    conn = sqlite3.connect(connection.DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    pw = None
    # find user id
    user = queries.get_user_by_username(conn, "int_cust")
    assert user is not None
    uid = user["id"]
    token = session_service.create_session_for_user(uid)

    # expire the session by updating expires_at to the past
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    cur.execute("UPDATE sessions SET expires_at = ? WHERE token = ?", (past, token))
    conn.commit()
    conn.close()

    # monkeypatch questionary.select to immediately choose Logout if dashboard is entered
    monkeypatch.setattr(questionary, "select", lambda *a, **k: DummyPrompt("Logout"))

    # call passenger dashboard with expired token — should detect expiry and return (auto logout)
    passenger_cli.passenger_dashboard("int_cust", session_token=token)

    # session should be deleted by validate_session cleanup
    conn = sqlite3.connect(connection.DB_PATH)
    conn.row_factory = sqlite3.Row
    s = queries.get_session(conn, token)
    assert s is None
    conn.close()
