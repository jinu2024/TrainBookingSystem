from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from database import connection, queries


SESSION_TTL = timedelta(hours=24)


def _now_iso() -> str:
    # timezone-aware UTC ISO timestamp
    return datetime.now(timezone.utc).isoformat()


def _expires_iso() -> str:
    # timezone-aware UTC ISO timestamp for expiry
    return (datetime.now(timezone.utc) + SESSION_TTL).isoformat()


def create_session_for_user(user_id: int) -> str:
    """Create a session token for given user_id and return the token."""
    token = uuid.uuid4().hex
    expires_at = _expires_iso()
    conn = connection.get_connection()
    try:
        queries.create_session(conn, token, user_id, expires_at)
        return token
    finally:
        connection.close_connection(conn)


def validate_session(token: str) -> dict:
    """Validate a session token and return the session row as dict.

    Raises ValueError if token is invalid or expired.
    """
    conn = connection.get_connection()
    try:
        now = _now_iso()
        # cleanup expired sessions first
        queries.delete_expired_sessions(conn, now)
        row = queries.get_session(conn, token)
        if not row:
            raise ValueError("Session invalid or expired")
        return dict(row)
    finally:
        connection.close_connection(conn)


def invalidate_session(token: str) -> None:
    conn = connection.get_connection()
    try:
        queries.delete_session(conn, token)
    finally:
        connection.close_connection(conn)
