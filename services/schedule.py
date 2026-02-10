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
    fare: float,
) -> int:
    """Create a schedule entry after validating inputs.

    travel_date: 'YYYY-MM-DD'
    departure_time / arrival_time: 'HH:MM'

    Returns the new schedule id.
    Raises ValueError on validation errors.
    """
    # Date validation
    try:
        datetime.strptime(travel_date, "%Y-%m-%d").date()
    except Exception:
        raise ValueError("travel_date must be in YYYY-MM-DD format")

    # Time validation
    try:
        datetime.strptime(departure_time, "%H:%M").time()
        datetime.strptime(arrival_time, "%H:%M").time()
    except Exception:
        raise ValueError("departure_time and arrival_time must be in HH:MM format")

    # Fare validation
    if fare is None:
        raise ValueError("fare is required")

    try:
        fare = float(fare)
    except Exception:
        raise ValueError("fare must be a number")

    if fare <= 0:
        raise ValueError("fare must be greater than zero")

    conn = connection.get_connection()
    try:
        return queries.create_schedule(
            conn,
            int(train_id),
            int(origin_station_id),
            int(destination_station_id),
            departure_time,
            arrival_time,
            travel_date,
            fare,
        )
    finally:
        connection.close_connection(conn)


def list_schedules() -> list:
    """Return all schedules as a list of rows."""
    conn = connection.get_connection()
    try:
        return queries.get_all_schedules(conn)
    finally:
        connection.close_connection(conn)
