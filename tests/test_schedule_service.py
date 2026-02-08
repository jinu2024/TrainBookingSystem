import sqlite3

from database import connection, queries
from services import train as train_service
from services import station as station_service
from services import schedule as schedule_service


def setup_temp_db(tmp_path):
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    conn = connection.get_connection()
    conn.close()
    return db_file


def test_create_and_find_schedule(tmp_path):
    setup_temp_db(tmp_path)

    # create train and stations
    tid = train_service.add_train("500X00", "Sched Tester")
    sid1 = station_service.add_station("ST0010", "Origin Station", "CityA")
    sid2 = station_service.add_station("ST0020", "Dest Station", "CityB")

    # create schedule
    sched_id = schedule_service.create_schedule(
        tid, sid1, sid2, "2026-02-10", "09:00", "12:00"
    )
    assert isinstance(sched_id, int)

    # verify via queries.find_schedules
    conn = sqlite3.connect(connection.DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = queries.find_schedules(conn, sid1, sid2, "2026-02-10")
    assert len(rows) == 1
    row = rows[0]
    assert row["train_number"] == "500X00"
    conn.close()
