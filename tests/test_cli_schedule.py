import sqlite3

import questionary

from database import connection, queries
from services import train as train_service
from services import station as station_service
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


def test_admin_schedule_flow(tmp_path, monkeypatch):
    setup_temp_db(tmp_path)

    # prepare data
    train_num = "800Z00"
    train_name = "CLI Schedule"
    tid = train_service.add_train(train_num, train_name)

    code1, name1 = "S10000", "Alpha"
    code2, name2 = "S20000", "Beta"
    sid1 = station_service.add_station(code1, name1, "CityX")
    sid2 = station_service.add_station(code2, name2, "CityY")

    # build display strings as admin CLI does
    train_display = f"{tid} - {train_num} - {train_name}"
    origin_display = f"{sid1} - {code1} - {name1}"
    dest_display = f"{sid2} - {code2} - {name2}"

    # monkeypatch questionary.select to return selections in order
    selects = [train_display, origin_display, dest_display]

    def fake_select(prompt, choices=None):
        return Dummy(selects.pop(0))

    monkeypatch.setattr(questionary, "select", fake_select)

    # monkeypatch text prompts for date/time
    texts = ["2026-02-11", "08:00", "11:00"]

    def fake_text(prompt):
        return Dummy(texts.pop(0))

    monkeypatch.setattr(questionary, "text", fake_text)

    # run the CLI scheduling action
    admin_cli.admin_schedule_new_train_jouney()

    # verify schedule created
    conn = sqlite3.connect(connection.DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = queries.find_schedules(conn, sid1, sid2, "2026-02-11")
    assert len(rows) == 1
    assert rows[0]["train_number"] == train_num
    conn.close()
