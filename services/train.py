from database import connection, queries
from utils.validators import is_valid_name


def add_train(train_number: str, train_name: str) -> int:
    if not isinstance(train_number, str) or len(train_number) != 6:
        raise ValueError("train_number must be a 6-character string")

    if not is_valid_name(train_name):
        raise ValueError(
            "Train name must be alphanumeric (letters, numbers, spaces only)"
        )

    conn = connection.get_connection()
    try:
        if queries.get_train_by_number(conn, train_number):
            raise ValueError("Train number already exists")

        return queries.create_train(conn, train_number, train_name)
    finally:
        connection.close_connection(conn)


def update_train(train_id: int, new_name: str) -> None:
    """Update train name by id with validation."""

    if not is_valid_name(new_name):
        raise ValueError(
            "Train name must be alphanumeric (letters, numbers, spaces only)"
        )

    conn = connection.get_connection()
    try:
        # Check train exists
        if not queries.get_train_by_id(conn, train_id):
            raise ValueError("Train does not exist")

        queries.update_train_name(conn, train_id, new_name.strip())

    finally:
        connection.close_connection(conn)



def remove_train(train_id: int) -> None:
    """Mark a train as inactive (soft delete)."""
    conn = connection.get_connection()
    try:
        queries.delete_train(conn, train_id)
    finally:
        connection.close_connection(conn)


def list_trains() -> list:
    """Return all trains as a list of rows."""
    conn = connection.get_connection()
    try:
        return queries.get_all_trains(conn)
    finally:
        connection.close_connection(conn)
