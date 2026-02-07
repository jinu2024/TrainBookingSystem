import sqlite3

import pytest

from database import connection, queries
from services import user as user_service
from utils import security


def setup_temp_db(tmp_path):
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    conn = connection.get_connection()
    conn.close()
    return db_file


def test_authenticate_admin_success(tmp_path):
    setup_temp_db(tmp_path)
    # create admin via service
    user_service.create_admin("admin1", "admin1@example.com", "strongpass")

    u = user_service.authenticate_user("admin1", "strongpass")
    assert u["username"] == "admin1"
    assert u["role"] == "admin"


def test_authenticate_customer_success(tmp_path):
    db_file = setup_temp_db(tmp_path)

    conn = connection.get_connection()
    pw = security.hash_password("custpass")
    queries.create_user(conn, "cust1", "cust1@example.com", pw, "customer")
    conn.close()

    u = user_service.authenticate_user("cust1", "custpass")
    assert u["username"] == "cust1"
    assert u["role"] == "customer"


def test_authenticate_invalid_password(tmp_path):
    setup_temp_db(tmp_path)
    user_service.create_admin("admin2", "admin2@example.com", "rightpass")

    with pytest.raises(ValueError):
        user_service.authenticate_user("admin2", "wrongpass")


def test_dashboards_exit_immediately(monkeypatch):
    # Make questionary.select return an object whose ask() returns 'Logout'
    import questionary

    class Dummy:
        def __init__(self, val):
            self._val = val

        def ask(self):
            return self._val


    def fake_select(prompt, choices=None):
        return Dummy("Logout")

    monkeypatch.setattr(questionary, "select", fake_select)

    # call admin and passenger dashboards; they should return after Logout
    from cli import admin as admin_cli
    from cli import passenger as passenger_cli

    admin_cli.admin_dashboard("admintest")
    passenger_cli.passenger_dashboard("pax")
