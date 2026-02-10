from __future__ import annotations

from datetime import datetime
import random
import string

from database import connection, queries


# -------------------------
# helpers (service-level)
# -------------------------

def _generate_booking_code() -> str:
    """
    Generate a unique-looking booking code.
    Example: BK20260210A9F3
    """
    date_part = datetime.now().strftime("%Y%m%d")
    rand_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"BK{date_part}{rand_part}"


# -------------------------
# booking services
# -------------------------

from datetime import datetime
import random
import string

from database import connection, queries


def _generate_booking_code() -> str:
    date_part = datetime.now().strftime("%Y%m%d")
    rand_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"BK{date_part}{rand_part}"


def book_ticket(
    *,
    username: str,
    train_id: int,
    origin_station_id: int,
    destination_station_id: int,
    travel_date: str,
    fare: float,
    payment: dict,   # 👈 payment info comes in
) -> dict:
    """
    Create booking + payment atomically.
    """
    if not username:
        raise ValueError("Username is required")

    try:
        datetime.strptime(travel_date, "%Y-%m-%d")
    except Exception:
        raise ValueError("travel_date must be YYYY-MM-DD")

    if origin_station_id == destination_station_id:
        raise ValueError("Origin and destination cannot be same")

    conn = connection.get_connection()
    try:
        # User
        user = queries.get_user_by_username(conn, username)
        if not user:
            raise ValueError("User not found")
        if user["role"] != "customer":
            raise ValueError("Only customers can book")

        # Train
        trains = queries.get_all_trains(conn)
        train = next(
            (t for t in trains if t["id"] == train_id and t["status"] == "active"),
            None,
        )
        if not train:
            raise ValueError("Train not found or inactive")

        # Schedule
        schedules = queries.find_schedules(
            conn, origin_station_id, destination_station_id, travel_date
        )
        if not any(s["train_id"] == train_id for s in schedules):
            raise ValueError("No valid schedule found")

        # Booking
        booking_code = _generate_booking_code()
        booking_id = queries.create_booking(
            conn,
            booking_code,
            user["id"],
            train_id,
            origin_station_id,
            destination_station_id,
            travel_date,
            fare,
        )

        # ✅ Payment (SAME CONNECTION)
        queries.create_payment(
            conn,
            booking_id=booking_id,
            amount=payment["amount"],
            method=payment["method"],
            status=payment["status"],          # success
            transaction_id=payment["transaction_id"],
        )

        return {
            "booking_id": booking_id,
            "booking_code": booking_code,
            "train_number": train["train_number"],
            "train_name": train["train_name"],
            "travel_date": travel_date,
            "fare": fare,
            "status": "confirmed",
        }

    finally:
        connection.close_connection(conn)


def get_booking_history(username: str) -> list:
    """
    Return booking history for a user.
    """
    if not username:
        raise ValueError("Username is required")

    conn = connection.get_connection()
    try:
        user = queries.get_user_by_username(conn, username)
        if not user:
            raise ValueError("User not found")

        return queries.get_bookings_by_user(conn, user["id"])

    finally:
        connection.close_connection(conn)


def cancel_booking_by_code(booking_code: str) -> None:
    """
    Cancel a booking and refund payment.
    """
    if not booking_code:
        raise ValueError("Booking code is required")

    conn = connection.get_connection()
    try:
        booking = queries.get_booking_by_code(conn, booking_code)
        if not booking:
            raise ValueError("Booking not found")

        if booking["status"] == "cancelled":
            raise ValueError("Booking is already cancelled")

        booking_id = booking["id"]

        # 1. Cancel booking
        queries.cancel_booking(conn, booking_code)

        # 2. Refund payment
        queries.refund_payment_by_booking_id(conn, booking_id)

    finally:
        connection.close_connection(conn)
