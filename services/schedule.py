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

    # departure must be before arrival (same-day journeys enforced here)
    if departure_time >= arrival_time:
        raise ValueError("departure_time must be earlier than arrival_time")

    conn = connection.get_connection()
    try:
        # validate train exists and is active
        train_row = queries.get_train_by_id(conn, int(train_id))
        if not train_row:
            raise ValueError("train_id does not exist")
        # train_row may be sqlite3.Row or tuple
        try:
            status = train_row["status"]
        except Exception:
            status = train_row[4] if len(train_row) > 4 else None
        if status != "active":
            raise ValueError("train is not active")

        # validate stations exist
        origin_row = queries.get_station_by_id(conn, int(origin_station_id))
        if not origin_row:
            raise ValueError("origin station does not exist")
        dest_row = queries.get_station_by_id(conn, int(destination_station_id))
        if not dest_row:
            raise ValueError("destination station does not exist")

        if int(origin_station_id) == int(destination_station_id):
            raise ValueError("origin and destination must be different")

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


from datetime import datetime
from utils.validators import is_valid_schedule_date, is_valid_time


def update_schedule(
    schedule_id: int,
    train_id: int,
    origin_station_id: int,
    destination_station_id: int,
    departure_date: str,
    arrival_date: str,
    departure_time: str,
    arrival_time: str,
    fare: float,
) -> None:
    """
    Update an existing schedule after validating inputs.

    Raises:
        ValueError on validation errors
    """

    # ================= BASIC VALIDATION =================

    if not is_valid_schedule_date(departure_date):
        raise ValueError("departure_date must be YYYY-MM-DD")

    if not is_valid_schedule_date(arrival_date):
        raise ValueError("arrival_date must be YYYY-MM-DD")

    if not is_valid_time(departure_time) or not is_valid_time(arrival_time):
        raise ValueError("Time must be HH:MM format")

    try:
        fare = float(fare)
        if fare < 0:
            raise ValueError
    except:
        raise ValueError("Fare must be positive number")

    # ================= DATETIME LOGIC =================

    dep_dt = datetime.strptime(f"{departure_date} {departure_time}", "%Y-%m-%d %H:%M")

    arr_dt = datetime.strptime(f"{arrival_date} {arrival_time}", "%Y-%m-%d %H:%M")

    if arr_dt <= dep_dt:
        raise ValueError("Arrival must be after departure")

    conn = connection.get_connection()

    try:
        # ================= EXISTENCE CHECKS =================

        if not queries.get_schedule_by_id(conn, int(schedule_id)):
            raise ValueError("schedule_id does not exist")

        train_row = queries.get_train_by_id(conn, int(train_id))
        if not train_row:
            raise ValueError("train_id does not exist")

        status = train_row.get("status") if isinstance(train_row, dict) else None
        print(f"Status: {status}")
        if status != "active":
            raise ValueError("train is not active")

        if not queries.get_station_by_id(conn, int(origin_station_id)):
            raise ValueError("origin station does not exist")

        if not queries.get_station_by_id(conn, int(destination_station_id)):
            raise ValueError("destination station does not exist")

        if int(origin_station_id) == int(destination_station_id):
            raise ValueError("origin and destination must be different")

        # ================= UPDATE =================

        queries.update_schedule(
            conn,
            int(schedule_id),
            int(train_id),
            int(origin_station_id),
            int(destination_station_id),
            departure_date,
            arrival_date,
            departure_time,
            arrival_time,
            float(fare),
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


def get_schedules_by_train(train_id: int) -> list:
    """Return all schedules for a specific train as a list of rows."""
    conn = connection.get_connection()
    try:
        return queries.get_schedules_by_train(conn, train_id)
    finally:
        connection.close_connection(conn)


def delete_schedule(schedule_id: int) -> None:
    """
    Delete schedule entry.
    """
    conn = connection.get_connection()
    try:
        queries.delete_schedule(conn, schedule_id)
    finally:
        connection.close_connection(conn)
