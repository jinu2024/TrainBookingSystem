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
        travel_dt = datetime.strptime(travel_date, "%Y-%m-%d").date()
    except Exception:
        raise ValueError("travel_date must be in YYYY-MM-DD format")

    try:
        dep_time_obj = datetime.strptime(departure_time, "%H:%M").time()
        arr_time_obj = datetime.strptime(arrival_time, "%H:%M").time()
    except Exception:
        raise ValueError("departure_time and arrival_time must be in HH:MM format")

    # departure must be before arrival (same-day journeys enforced here)
    if dep_time_obj >= arr_time_obj:
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
        )
    finally:
        connection.close_connection(conn)


def update_schedule(
    schedule_id: int,
    train_id: int,
    origin_station_id: int,
    destination_station_id: int,
    travel_date: str,
    departure_time: str,
    arrival_time: str,
) -> None:
    """Update an existing schedule after validating inputs.

    Raises:
        ValueError on validation errors
    """

    # ================= VALIDATION =================

    try:
        travel_dt = datetime.strptime(travel_date, "%Y-%m-%d").date()
    except Exception:
        raise ValueError("travel_date must be in YYYY-MM-DD format")

    try:
        dep_time_obj = datetime.strptime(departure_time, "%H:%M").time()
        arr_time_obj = datetime.strptime(arrival_time, "%H:%M").time()
    except Exception:
        raise ValueError("departure_time and arrival_time must be in HH:MM format")

    if dep_time_obj >= arr_time_obj:
        raise ValueError("departure_time must be earlier than arrival_time")

    conn = connection.get_connection()

    try:
        # ========== validate schedule exists ==========
        sched = queries.get_schedule_by_id(conn, int(schedule_id))
        if not sched:
            raise ValueError("schedule_id does not exist")

        # ========== validate train ==========
        train_row = queries.get_train_by_id(conn, int(train_id))
        if not train_row:
            raise ValueError("train_id does not exist")

        try:
            status = train_row["status"]
        except Exception:
            status = train_row[4] if len(train_row) > 4 else None

        if status != "active":
            raise ValueError("train is not active")

        # ========== validate stations ==========
        origin_row = queries.get_station_by_id(conn, int(origin_station_id))
        if not origin_row:
            raise ValueError("origin station does not exist")

        dest_row = queries.get_station_by_id(conn, int(destination_station_id))
        if not dest_row:
            raise ValueError("destination station does not exist")

        if int(origin_station_id) == int(destination_station_id):
            raise ValueError("origin and destination must be different")

        # ========== UPDATE ==========
        queries.update_schedule(
            conn,
            int(schedule_id),
            int(train_id),
            int(origin_station_id),
            int(destination_station_id),
            departure_time,
            arrival_time,
            travel_date,
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
