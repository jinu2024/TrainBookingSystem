import sqlite3

from database import connection, queries
from services import user as user_service


def setup_temp_db(tmp_path):
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    conn = connection.get_connection()
    conn.close()
    return db_file


def test_passenger_list_add_update_remove(tmp_path):
    setup_temp_db(tmp_path)

    res = user_service.create_customer(
        "puser", "puser@example.com", "pass1234", full_name="P User", dob="1990-01-01", gender="male"
    )
    uid = res["id"]

    # list initially empty
    lst = user_service.list_passengers(uid)
    assert lst == []

    # add passenger
    p = {"name": "Child One", "dob": "2010-05-05", "gender": "female"}
    updated = user_service.add_passenger(uid, p)
    assert len(updated) == 1
    assert updated[0]["name"] == "Child One"

    # update passenger
    newp = {"name": "Child One Jr", "dob": "2010-05-05", "gender": "female"}
    updated2 = user_service.update_passenger(uid, 0, newp)
    assert updated2[0]["name"] == "Child One Jr"

    # remove passenger
    updated3 = user_service.remove_passenger(uid, 0)
    assert updated3 == []


def test_update_out_of_range_raises(tmp_path):
    setup_temp_db(tmp_path)
    res = user_service.create_customer(
        "puser2", "puser2@example.com", "pass1234", full_name="P2", dob="1992-02-02", gender="other"
    )
    uid = res["id"]

    try:
        user_service.update_passenger(uid, 0, {"name": "x"})
        assert False, "expected IndexError"
    except IndexError:
        pass
