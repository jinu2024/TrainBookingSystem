from database import connection, queries


def add_station(code: str, name: str, city: str) -> int:
    """Add a station and return its id. Raises ValueError if code exists."""
    # validate station code format (6 chars expected)
    if not isinstance(code, str) or len(code) != 6:
        print(f"Invalid station code: {code}")
        raise ValueError("station code must be a 6-character string")
    conn = connection.get_connection()
    try:
        if queries.get_station_by_code(conn, code):
            raise ValueError("Station code already exists")
        return queries.create_station(conn, code, name, city)
    finally:
        connection.close_connection(conn)


def update_station(station_id: int, new_station_name: str) -> None:
    """Update station name by id."""
    conn = connection.get_connection()
    try:
        queries.update_station_name(conn, station_id, new_station_name)
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
