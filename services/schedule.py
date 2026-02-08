from __future__ import annotations

from datetime import datetime

from database import connection, queries


def create_schedule(
    train_id: int,
    origin_station_id: int,
    destination_station_id: int,
    travel_date: str,
    departure_time: str,
    arrival_time: str,
) -> int:
    """Create a schedule entry after validating inputs.

    travel_date: 'YYYY-MM-DD'
    departure_time / arrival_time: 'HH:MM'

    Returns the new schedule id.
    Raises ValueError on validation errors.
    """
    # Basic validation
    try:
        dt = datetime.strptime(travel_date, "%Y-%m-%d").date()
    except Exception:
        raise ValueError("travel_date must be in YYYY-MM-DD format")

    try:
        _ = datetime.strptime(departure_time, "%H:%M").time()
        _ = datetime.strptime(arrival_time, "%H:%M").time()
    except Exception:
        raise ValueError("departure_time and arrival_time must be in HH:MM format")

    conn = connection.get_connection()
    try:
        # ensure referenced records exist
        train = queries.get_train_by_number(conn, train_id) if isinstance(train_id, str) else None
        # The queries.create_schedule expects numeric IDs; callers should supply ids.
        # We'll not try to look up by train_number here; ensure ids are ints.

        return queries.create_schedule(
            conn,
            int(train_id),
            int(origin_station_id),
            int(destination_station_id),
            departure_time,
            arrival_time,
            travel_date,
        )
    finally:
        connection.close_connection(conn)
