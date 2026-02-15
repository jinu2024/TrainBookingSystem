from database import connection, queries
from utils.validators import is_valid_name


def add_station(code: str, name: str, city: str) -> int:

    if not isinstance(code, str) or len(code) != 6:
        raise ValueError("station code must be a 6-character string")

    if not is_valid_name(name):
        raise ValueError(
            "Station name must be alphanumeric (letters, numbers, spaces only)"
        )

    conn = connection.get_connection()
    try:
        if queries.get_station_by_code(conn, code):
            raise ValueError("Station code already exists")

        return queries.create_station(conn, code, name, city)
    finally:
        connection.close_connection(conn)


def update_station(station_id: int, new_station_name: str) -> None:
    """Update station name by id with validation."""

    if not is_valid_name(new_station_name):
        raise ValueError(
            "Station name must be alphanumeric (letters, numbers, spaces only)"
        )

    conn = connection.get_connection()
    try:
        # Check station exists
        if not queries.get_station_by_id(conn, station_id):
            raise ValueError("Station does not exist")

        queries.update_station_name(conn, station_id, new_station_name.strip())

    finally:
        connection.close_connection(conn)


def remove_train(station_id: int) -> None:
    """Mark a train as inactive (soft delete)."""
    conn = connection.get_connection()
    try:
        queries.delete_train(conn, station_id)
    finally:
        connection.close_connection(conn)


def list_stations() -> list:
    conn = connection.get_connection()
    try:
        return queries.get_all_stations(conn)
    finally:
        connection.close_connection(conn)
