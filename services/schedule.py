from __future__ import annotations

from datetime import datetime,timedelta

from database import connection, queries
from utils.validators import is_valid_schedule_date, is_valid_time



def create_schedule(
    train_id: int,
    origin_station_id: int,
    destination_station_id: int,
    departure_date: str,
    arrival_date: str,
    departure_time: str,
    arrival_time: str,
    fare: float,
) -> int:

    # ================= FARE VALIDATION =================
    try:
        fare = float(fare)
    except:
        raise ValueError("Fare must be a number")

    if fare < 50:
        raise ValueError("Minimum fare must be ₹50")

    if fare > 400000:
        raise ValueError("Maximum fare cannot exceed ₹4,00,000")

    # ================= DATETIME VALIDATION =================
    dep_dt = datetime.strptime(
        f"{departure_date} {departure_time}",
        "%Y-%m-%d %H:%M",
    )

    arr_dt = datetime.strptime(
        f"{arrival_date} {arrival_time}",
        "%Y-%m-%d %H:%M",
    )

    if arr_dt <= dep_dt:
        raise ValueError("Arrival must be after departure")

    duration = arr_dt - dep_dt

    if duration < timedelta(minutes=30):
        raise ValueError("Minimum journey duration must be 30 minutes")

    if duration > timedelta(days=31):
        raise ValueError("Journey duration cannot exceed 1 month")

    # ================= DATABASE VALIDATION =================
    conn = connection.get_connection()

    try:
        if not queries.get_train_by_id(conn, train_id):
            raise ValueError("train_id does not exist")

        if not queries.get_station_by_id(conn, origin_station_id):
            raise ValueError("origin station does not exist")

        if not queries.get_station_by_id(conn, destination_station_id):
            raise ValueError("destination station does not exist")

        if origin_station_id == destination_station_id:
            raise ValueError("origin and destination must be different")

        return queries.create_schedule(
            conn,
            train_id,
            origin_station_id,
            destination_station_id,
            departure_date,
            arrival_date,
            departure_time,
            arrival_time,
            fare,
        )

    finally:
        connection.close_connection(conn)



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

    Business Rules:
    - Fare must be between ₹50 and ₹4,00,000
    - Minimum journey duration: 30 minutes
    - Maximum journey duration: 1 month
    - Arrival must be after departure
    """

    # ================= BASIC DATE VALIDATION =================

    if not is_valid_schedule_date(departure_date):
        raise ValueError("departure_date must be YYYY-MM-DD")

    if not is_valid_schedule_date(arrival_date):
        raise ValueError("arrival_date must be YYYY-MM-DD")

    if not is_valid_time(departure_time):
        raise ValueError("departure_time must be HH:MM format")

    if not is_valid_time(arrival_time):
        raise ValueError("arrival_time must be HH:MM format")

    # ================= FARE VALIDATION =================

    try:
        fare = float(fare)
    except Exception:
        raise ValueError("Fare must be a number")

    if fare < 50:
        raise ValueError("Minimum fare must be ₹50")

    if fare > 400000:
        raise ValueError("Maximum fare cannot exceed ₹4,00,000")

    # ================= DATETIME LOGIC =================

    dep_dt = datetime.strptime(
        f"{departure_date} {departure_time}",
        "%Y-%m-%d %H:%M"
    )

    arr_dt = datetime.strptime(
        f"{arrival_date} {arrival_time}",
        "%Y-%m-%d %H:%M"
    )

    if arr_dt <= dep_dt:
        raise ValueError("Arrival must be after departure")

    duration = arr_dt - dep_dt

    if duration < timedelta(minutes=30):
        raise ValueError("Minimum journey duration must be 30 minutes")

    if duration > timedelta(days=31):
        raise ValueError("Journey duration cannot exceed 1 month")

    # ================= DATABASE VALIDATION =================

    conn = connection.get_connection()

    try:
        # Schedule existence
        if not queries.get_schedule_by_id(conn, int(schedule_id)):
            raise ValueError("schedule_id does not exist")

        # Train validation
        train_row = queries.get_train_by_id(conn, int(train_id))
        if not train_row:
            raise ValueError("train_id does not exist")

        # Handle both dict and tuple row formats
        if isinstance(train_row, dict):
            status = train_row.get("status")
        else:
            # assuming tuple: (id, train_number, train_name, status)
            status = train_row[3] if len(train_row) >= 4 else None

        # Treat NULL as active (optional business rule)
        if not status:
            status = "active"

        if status != "active":
            raise ValueError("train is not active")

        # Station validation
        if not queries.get_station_by_id(conn, int(origin_station_id)):
            raise ValueError("origin station does not exist")

        if not queries.get_station_by_id(conn, int(destination_station_id)):
            raise ValueError("destination station does not exist")

        if int(origin_station_id) == int(destination_station_id):
            raise ValueError("origin and destination must be different")

        # ================= UPDATE EXECUTION =================

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


def get_schedules_by_train(train_id: int) -> list:
    """Return all schedules for a specific train as a list of rows."""
    conn = connection.get_connection()
    try:
        return queries.get_schedules_by_train(conn, train_id)
    finally:
        connection.close_connection(conn)

def delete_schedule(schedule_id: int) -> None:

    conn = connection.get_connection()

    try:
        schedule = queries.get_schedule_by_id(conn, schedule_id)

        if not schedule:
            raise ValueError("Schedule does not exist")

        train_id = schedule["train_id"]
        origin_id = schedule["origin_station_id"]
        dest_id = schedule["destination_station_id"]
        departure_date = schedule["departure_date"]

        if queries.booking_exists_for_schedule(
            conn,
            train_id,
            origin_id,
            dest_id,
            departure_date,
        ):
            raise ValueError(
                "Cannot delete schedule. Bookings exist for this journey."
            )

        queries.delete_schedule(conn, schedule_id)

    finally:
        connection.close_connection(conn)
