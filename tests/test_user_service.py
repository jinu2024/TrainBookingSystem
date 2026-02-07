import os
import sqlite3
import importlib

import pytest

from services import user as user_service
from database import connection, queries


def setup_temp_db(tmp_path):
    # point the connection module to a temp DB file for isolation
    db_file = tmp_path / "test.db"
    connection.DB_PATH = db_file
    # ensure tables
    conn = connection.get_connection()
    conn.close()
    return db_file


def test_create_admin_success(tmp_path):
    db_file = setup_temp_db(tmp_path)

    res = user_service.create_admin("alice", "alice@example.com", "strongpass")
    assert res["username"] == "alice"

    # verify row exists
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    row = queries.get_user_by_username(conn, "alice")
    assert row is not None
    assert row["email"] == "alice@example.com"
    conn.close()


def test_create_admin_duplicate_username(tmp_path):
    setup_temp_db(tmp_path)

    user_service.create_admin("bob", "bob@example.com", "password123")
    with pytest.raises(ValueError):
        user_service.create_admin("bob", "bob2@example.com", "anotherpass")


def test_create_admin_invalid_password(tmp_path):
    setup_temp_db(tmp_path)
    with pytest.raises(ValueError):
        user_service.create_admin("charlie", "charlie@example.com", "short")


def test_create_customer_success(tmp_path):
    db_file = setup_temp_db(tmp_path)

    res = user_service.create_customer("custalice", "custalice@example.com", "custstrong")
    assert res["username"] == "custalice"

    # verify row exists
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    row = queries.get_user_by_username(conn, "custalice")
    assert row is not None
    assert row["email"] == "custalice@example.com"
    assert row["role"] == "customer"
    conn.close()
