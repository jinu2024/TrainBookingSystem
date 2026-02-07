import sqlite3
from datetime import datetime, timedelta

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
    conn = connection.get_connection()
    pw = security.hash_password("custpass")
    uid = queries.create_user(conn, "suser", "suser@example.com", pw, "customer")
    conn.close()

    token = session_service.create_session_for_user(uid)
    # validate
    s = session_service.validate_session(token)
    assert s["user_id"] == uid


def test_session_expiry(tmp_path):
    db_file = setup_temp_db(tmp_path)

    conn = connection.get_connection()
    pw = security.hash_password("custpass")
    uid = queries.create_user(conn, "suser2", "suser2@example.com", pw, "customer")

    # insert expired session
    expired = (datetime.utcnow() - timedelta(days=1)).isoformat()
    token = "expiredtoken123"
    queries.create_session(conn, token, uid, expired)
    conn.close()

    try:
        session_service.validate_session(token)
        assert False, "expected session to be invalid"
    except ValueError:
        pass
