import sqlite3
from datetime import datetime, timedelta, timezone
from services import user as user_service

from database import connection, queries
from services import session as session_service
from utils import security


def setup_temp_db(tmp_path):
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    conn = connection.get_connection()
    conn.close()
    return db_file


def test_create_and_validate_session(tmp_path):
    db_file = setup_temp_db(tmp_path)

    # create a user
    # create a customer via service with required profile fields
    res = user_service.create_customer("suser", "suser@example.com", "custpass", full_name="S User", dob="1990-01-01", gender="male")
    uid = res["id"]

    token = session_service.create_session_for_user(uid)
    # validate
    s = session_service.validate_session(token)
    assert s["user_id"] == uid


def test_session_expiry(tmp_path):
    db_file = setup_temp_db(tmp_path)

    res = user_service.create_customer("suser2", "suser2@example.com", "custpass2", full_name="S User2", dob="1991-01-01", gender="female")
    uid = res["id"]

    # insert expired session
    expired = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    token = "expiredtoken123"
    conn = connection.get_connection()
    queries.create_session(conn, token, uid, expired)
    conn.close()

    try:
        session_service.validate_session(token)
        assert False, "expected session to be invalid"
    except ValueError:
        pass
