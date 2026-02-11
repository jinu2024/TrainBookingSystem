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
    payment: dict,
) -> dict:
    """
    Create booking + payment atomically.
    """

    if not username:
        raise ValueError("Username is required")

    # Validate date format
    try:
        datetime.strptime(travel_date, "%Y-%m-%d")
    except Exception:
        raise ValueError("travel_date must be YYYY-MM-DD")

    if origin_station_id == destination_station_id:
        raise ValueError("Origin and destination cannot be same")

    if not payment or payment.get("status") != "success":
        raise ValueError("Payment not successful")

    conn = connection.get_connection()

    try:
        # -------------------------
        # USER VALIDATION
        # -------------------------
        user = queries.get_user_by_username(conn, username)
        if not user:
            raise ValueError("User not found")

        if user["role"] != "customer":
            raise ValueError("Only customers can book tickets")

        # -------------------------
        # TRAIN VALIDATION
        # -------------------------
        train = queries.get_train_by_id(conn, train_id)
        if not train or train["status"] != "active":
            raise ValueError("Train not found or inactive")

        # -------------------------
        # SCHEDULE VALIDATION
        # -------------------------
        schedules = queries.find_schedules(
            conn,
            origin_station_id,
            destination_station_id,
            travel_date,
        )

        schedule = next(
            (s for s in schedules if s["train_id"] == train_id),
            None,
        )

        if not schedule:
            raise ValueError("No valid schedule found for selected train")

        # ✅ REAL fare from DB
        actual_fare = schedule["fare"]

        # -------------------------
        # CREATE BOOKING
        # -------------------------
        booking_code = _generate_booking_code()

        booking_id = queries.create_booking(
            conn,
            booking_code,
            user["id"],
            train_id,
            origin_station_id,
            destination_station_id,
            travel_date,
            actual_fare,      
        )

        # -------------------------
        # CREATE PAYMENT
        # -------------------------
        queries.create_payment(
            conn,
            booking_id=booking_id,
            amount=payment["amount"],
            method=payment["method"],
            status=payment["status"],
            transaction_id=payment["transaction_id"],
        )

        return {
            "booking_id": booking_id,
            "booking_code": booking_code,
            "train_number": train["train_number"],
            "train_name": train["train_name"],
            "departure_time": schedule["departure_time"],
            "arrival_time": schedule["arrival_time"],
            "departure_date": schedule["departure_date"],
            "arrival_date": schedule["arrival_date"],
            "fare": actual_fare,
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


from datetime import datetime, timedelta


def cancel_booking_by_code(booking_code: str) -> dict:
    """
    Cancel a booking and apply smart refund logic.
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

        # ---------------------------------------
        # Get full booking details with schedule
        # ---------------------------------------
        full_booking = queries.get_bookings_by_user(conn, booking["user_id"])

        booking_row = next(
            (b for b in full_booking if b["booking_code"] == booking_code),
            None,
        )

        if not booking_row:
            raise ValueError("Schedule details not found")

        # ---------------------------------------
        # Calculate departure datetime
        # ---------------------------------------
        departure_str = (
            f"{booking_row['departure_date']} "
            f"{booking_row['departure_time']}"
        )

        departure_dt = datetime.strptime(
            departure_str,
            "%Y-%m-%d %H:%M",
        )

        now = datetime.now()

        time_diff = departure_dt - now
        hours_remaining = time_diff.total_seconds() / 3600

        original_amount = booking_row["fare"]

        # ---------------------------------------
        # Refund Logic
        # ---------------------------------------
        if hours_remaining >= 6:
            refund_amount = original_amount
            deduction = 0
        else:
            deduction = round(original_amount * 0.10, 2)
            refund_amount = round(original_amount - deduction, 2)

        # ---------------------------------------
        # Update booking + payment
        # ---------------------------------------
        queries.cancel_booking(conn, booking_code)
        queries.refund_payment_by_booking_id(conn, booking_id)

        return {
            "original_amount": original_amount,
            "refund_amount": refund_amount,
            "deduction": deduction,
            "hours_remaining": round(hours_remaining, 2),
        }

    finally:
        connection.close_connection(conn)
