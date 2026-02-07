import sqlite3

from database import connection, queries
from services import train as train_service


def setup_temp_db(tmp_path):
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    conn = connection.get_connection()
    conn.close()
    return db_file


def test_add_and_list_trains(tmp_path):
    setup_temp_db(tmp_path)

    tid = train_service.add_train("100A", "Morning Express")
    assert isinstance(tid, int)

    rows = train_service.list_trains()
    assert any(r["train_number"] == "100A" for r in rows)


def test_add_duplicate_train_number(tmp_path):
    setup_temp_db(tmp_path)
    train_service.add_train("200B", "Night Rider")
    try:
        train_service.add_train("200B", "Duplicate")
        assert False, "expected ValueError for duplicate train number"
    except ValueError:
        pass


def test_update_and_remove_train(tmp_path):
    setup_temp_db(tmp_path)
    tid = train_service.add_train("300C", "Regional")

    # update name
    train_service.update_train(tid, "Regional Updated")
    conn = sqlite3.connect(connection.DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM trains WHERE id = ?", (tid,))
    row = cur.fetchone()
    assert row["train_name"] == "Regional Updated"

    # remove (soft-delete)
    train_service.remove_train(tid)
    cur.execute("SELECT * FROM trains WHERE id = ?", (tid,))
    row = cur.fetchone()
    assert row["status"] == "inactive"
    conn.close()
