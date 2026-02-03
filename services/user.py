"""User service: business logic for user management (registration, lookup).

Keep logic side-effect free where possible; database operations are delegated to
`database/queries.py` via `database/connection.py`.
"""
from __future__ import annotations

import hashlib
from typing import Optional

from database import connection, queries
from utils.validators import is_valid_email, is_strong_password


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_admin(username: str, email: str, password: str) -> dict:
    """Create an admin user.

    Returns a dict with `id` and `username` on success.
    Raises ValueError for validation failures or RuntimeError for DB errors.
    """
    if not username:
        raise ValueError("username required")
    if not is_valid_email(email):
        raise ValueError("invalid email")
    if not is_strong_password(password):
        raise ValueError("password must be at least 8 characters")

    conn = connection.get_connection()
    try:
        # ensure uniqueness
        if queries.get_user_by_username(conn, username):
            raise ValueError("username already exists")
        if queries.get_user_by_email(conn, email):
            raise ValueError("email already exists")

        password_hash = _hash_password(password)
        user_id = queries.create_user(conn, username, email, password_hash, role="admin")
        return {"id": user_id, "username": username}
    finally:
        connection.close_connection(conn)
