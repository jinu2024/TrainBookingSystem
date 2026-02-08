import sqlite3

import questionary

from database import connection, queries
from services import train as train_service
from cli import admin as admin_cli


def setup_temp_db(tmp_path):
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    conn = connection.get_connection()
    conn.close()
    return db_file


class Dummy:
    def __init__(self, val):
        self._val = val

    def ask(self):
        return self._val


def test_admin_register_train_and_view(tmp_path, monkeypatch):
    setup_temp_db(tmp_path)

    # monkeypatch questionary.text to provide train number and name
    seq = ["700Z00", "Test Line"]

    def fake_text(prompt):
        return Dummy(seq.pop(0))

    monkeypatch.setattr(questionary, "text", fake_text)

    # call registration
    admin_cli.admin_train_registration()

    # verify train exists
    conn = sqlite3.connect(connection.DB_PATH)
    conn.row_factory = sqlite3.Row
    row = queries.get_train_by_number(conn, "700Z00")
    assert row is not None
    assert row["train_name"] == "Test Line"
    conn.close()
