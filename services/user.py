"""User service: business logic for user management (registration, lookup).

Keep logic side-effect free where possible; database operations are delegated to
`database/queries.py` via `database/connection.py`.
"""
from __future__ import annotations
from typing import Optional

from database import connection, queries
from utils.validators import is_valid_email, is_strong_password
from utils.security import hash_password,verify_password
import json


def create_admin(username: str, email: str, password: str, *, full_name: str | None = None, dob: str | None = None, gender: str | None = None, mobile: str | None = None, aadhaar: str | None = None, nationality: str | None = None, address: str | None = None, passengers: str | None = None) -> dict:
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

        password_hash = hash_password(password)
        user_id = queries.create_user(
            conn,
            username,
            email,
            password_hash,
            role="admin",
            full_name=full_name,
            dob=dob,
            gender=gender,
            mobile=mobile,
            aadhaar=aadhaar,
            nationality=nationality,
            address=address,
            passengers=passengers,
        )
        return {"id": user_id, "username": username}
    finally:
        connection.close_connection(conn)


def create_customer(username: str, email: str | None, password: str, *, full_name: str | None = None, dob: str | None = None, gender: str | None = None, mobile: str | None = None, aadhaar: str | None = None, nationality: str | None = None, address: str | None = None, passengers: str | None = None) -> dict:
    """Create a customer user.

    Same validation rules as admin, but role is 'customer'.
    """
    if not username:
        raise ValueError("username required")
    # email or mobile must be provided for customers
    if not email and not mobile:
        raise ValueError("email or mobile number is required")
    if email and not is_valid_email(email):
        raise ValueError("invalid email")
    if not is_strong_password(password):
        raise ValueError("password must be at least 8 characters")
    # require minimal profile fields for customers
    if not full_name:
        raise ValueError("full name is required for customer signup")
    if not dob:
        raise ValueError("date of birth (dob) is required for customer signup")
    if not gender:
        raise ValueError("gender is required for customer signup")

    conn = connection.get_connection()
    try:
        if queries.get_user_by_username(conn, username):
            raise ValueError("username already exists")
        if email and queries.get_user_by_email(conn, email):
            raise ValueError("email already exists")
        if mobile and queries.get_user_by_mobile(conn, mobile):
            raise ValueError("mobile already exists")

        password_hash = hash_password(password)
        user_id = queries.create_user(
            conn,
            username,
            email,
            password_hash,
            role="customer",
            full_name=full_name,
            dob=dob,
            gender=gender,
            mobile=mobile,
            aadhaar=aadhaar,
            nationality=nationality,
            address=address,
            passengers=passengers,
        )
        return {"id": user_id, "username": username}
    finally:
        connection.close_connection(conn)


def authenticate_admin(username: str, password: str) -> dict:
    """
    Authenticate an admin user.
    Returns user dict on success.
    Raises ValueError on failure.
    """
    if not username or not password:
        raise ValueError("username and password required")

    conn = connection.get_connection()
    try:
        user = queries.get_user_by_username(conn, username)

        if not user:
            raise ValueError("Invalid username or password")

        if user["role"] != "admin":
            raise ValueError("Unauthorized access")

        if user["status"] != "active":
            raise ValueError("Admin account is inactive")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid username or password")

        return dict(user)

    finally:
        connection.close_connection(conn)


def authenticate_customer(username: str, password: str) -> dict:
    """
    Authenticate a customer user.
    """
    if not username or not password:
        raise ValueError("username and password required")

    conn = connection.get_connection()
    try:
        user = queries.get_user_by_username(conn, username)

        if not user:
            raise ValueError("Invalid username or password")

        if user["role"] != "customer":
            raise ValueError("Unauthorized access")

        if user["status"] != "active":
            raise ValueError("Customer account is inactive")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid username or password")

        return dict(user)

    finally:
        connection.close_connection(conn)


def authenticate_user(identifier: str, password: str) -> dict:
    """Generic authenticate: identifier may be username or email.

    Returns user dict on success. Raises ValueError on failure.
    """
    if not identifier or not password:
        raise ValueError("identifier and password required")

    conn = connection.get_connection()
    try:
        # try username first, then email
        user = queries.get_user_by_username(conn, identifier)
        if not user:
            user = queries.get_user_by_email(conn, identifier)

        if not user:
            raise ValueError("Invalid credentials")

        if user["status"] != "active":
            raise ValueError("Account is inactive")

        if not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid credentials")

        return dict(user)

    finally:
        connection.close_connection(conn)


### Passenger list helpers (JSON stored in users.passengers)
def list_passengers(user_id: int) -> list:
    """Return a list of passenger dicts for the given user.

    If no passengers are stored, returns an empty list.
    """
    conn = connection.get_connection()
    try:
        raw = queries.get_passengers_for_user(conn, user_id)
        if not raw:
            return []
        try:
            return json.loads(raw)
        except Exception:
            # corrupted JSON -> return empty list to avoid crashes
            return []
    finally:
        connection.close_connection(conn)


def add_passenger(user_id: int, passenger: dict) -> list:
    """Add a passenger (dict) to the user's passengers list and return updated list."""
    conn = connection.get_connection()
    try:
        current = queries.get_passengers_for_user(conn, user_id)
        if not current:
            lst = []
        else:
            try:
                lst = json.loads(current)
            except Exception:
                lst = []

        lst.append(passenger)
        queries.save_passengers_for_user(conn, user_id, json.dumps(lst))
        return lst
    finally:
        connection.close_connection(conn)


def update_passenger(user_id: int, index: int, passenger: dict) -> list:
    """Update passenger at 0-based index. Returns updated list.

    Raises IndexError if index is out of range.
    """
    conn = connection.get_connection()
    try:
        current = queries.get_passengers_for_user(conn, user_id)
        if not current:
            raise IndexError("no passengers to update")
        try:
            lst = json.loads(current)
        except Exception:
            raise IndexError("passenger list corrupted")

        if index < 0 or index >= len(lst):
            raise IndexError("passenger index out of range")

        lst[index] = passenger
        queries.save_passengers_for_user(conn, user_id, json.dumps(lst))
        return lst
    finally:
        connection.close_connection(conn)


def remove_passenger(user_id: int, index: int) -> list:
    """Remove passenger at 0-based index. Returns updated list.

    Raises IndexError if index is out of range.
    """
    conn = connection.get_connection()
    try:
        current = queries.get_passengers_for_user(conn, user_id)
        if not current:
            raise IndexError("no passengers to remove")
        try:
            lst = json.loads(current)
        except Exception:
            raise IndexError("passenger list corrupted")

        if index < 0 or index >= len(lst):
            raise IndexError("passenger index out of range")

        lst.pop(index)
        queries.save_passengers_for_user(conn, user_id, json.dumps(lst))
        return lst
    finally:
        connection.close_connection(conn)
