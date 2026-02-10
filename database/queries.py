"""SQL queries and helpers for TrainBookingSystem."""

from database.connection import get_connection
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema.sql"


def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        with open(SCHEMA_PATH, "r") as f:
            cursor.executescript(f.read())

        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")

    except Exception as e:
        print("❌ Database initialization failed:", e)


# USER QUERIES


def create_user(
    conn,
    username,
    email,
    password_hash,
    role,
    full_name=None,
    dob=None,
    gender=None,
    mobile=None,
    aadhaar=None,
    nationality=None,
    address=None,
    passengers=None,
):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (
            username, email, mobile, password_hash, role,
            full_name, dob, gender, aadhaar, nationality, address, passengers
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            email,
            mobile,
            password_hash,
            role,
            full_name,
            dob,
            gender,
            aadhaar,
            nationality,
            address,
            passengers,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def get_user_by_username(conn, username):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchone()


def get_user_by_email(conn, email):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()


def get_user_by_mobile(conn, mobile):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    return cursor.fetchone()


# -------------------------
# STATION QUERIES
# -------------------------


def create_station(conn, code, name, city):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO stations (code, name, city)
        VALUES (?, ?, ?)
        """,
        (code, name, city),
    )
    conn.commit()
    return cur.lastrowid


def get_station_by_code(conn, code):
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM stations WHERE code = ?",
        (code,),
    )
    return cur.fetchone()


def get_all_stations(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM stations")
    return cur.fetchall()


# -------------------------
# TRAIN QUERIES
# -------------------------


def create_train(conn, train_number, train_name):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO trains (train_number, train_name)
        VALUES (?, ?)
        """,
        (train_number, train_name),
    )
    conn.commit()
    return cur.lastrowid


def update_train_name(conn, train_id, new_train_name):
    cur = conn.cursor()
    cur.execute(
        "UPDATE trains SET train_name = ? WHERE id = ?", (new_train_name, train_id)
    )
    conn.commit()


def update_station_name(conn, station_id, new_station_name):
    cur = conn.cursor()
    # update the station name (not the code)
    cur.execute(
        "UPDATE stations SET name = ? WHERE id = ?", (new_station_name, station_id)
    )
    conn.commit()


def get_train_by_number(conn, train_number):
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM trains WHERE train_number = ?",
        (train_number,),
    )
    return cur.fetchone()


def get_all_trains(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM trains")
    return cur.fetchall()


def delete_train(conn, train_id):
    cur = conn.cursor()
    cur.execute(
        "UPDATE trains SET status = 'inactive' WHERE id = ?",
        (train_id,),
    )
    conn.commit()


# -------------------------
# SCHEDULE QUERIES
# -------------------------


def create_schedule(
    conn,
    train_id,
    origin_station_id,
    destination_station_id,
    departure_time,
    arrival_time,
    travel_date,
    fare,
):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO schedules (
            train_id,
            origin_station_id,
            destination_station_id,
            departure_time,
            arrival_time,
            travel_date,
            fare
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            train_id,
            origin_station_id,
            destination_station_id,
            departure_time,
            arrival_time,
            travel_date,
            fare,
        ),
    )
    conn.commit()
    return cur.lastrowid


def find_schedules(conn, origin_id, destination_id, travel_date):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            s.id,
            s.train_id,
            s.origin_station_id,
            s.destination_station_id,
            s.departure_time,
            s.arrival_time,
            s.travel_date,
            s.fare,
            t.train_number,
            t.train_name
        FROM schedules s
        JOIN trains t ON s.train_id = t.id
        WHERE s.origin_station_id = ?
          AND s.destination_station_id = ?
          AND s.travel_date = ?
          AND t.status = 'active'
        """,
        (origin_id, destination_id, travel_date),
    )
    return cur.fetchall()


def get_all_schedules(conn):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * from schedules
        """
    )
    return cur.fetchall()


# -------------------------
# SESSION QUERIES
# -------------------------


def create_session(conn, token, user_id, expires_at):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO sessions (token, user_id, expires_at)
        VALUES (?, ?, ?)
        """,
        (token, user_id, expires_at),
    )
    conn.commit()


def get_session(conn, token):
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE token = ?", (token,))
    return cur.fetchone()


def delete_session(conn, token):
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()


def delete_expired_sessions(conn, now_iso):
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE expires_at <= ?", (now_iso,))
    conn.commit()


def get_active_session(conn, now_iso):
    """Return the most recent active session (not expired) joined with user info.

    Returns a row with token, user_id, expires_at, username, role or None.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.token, s.user_id, s.expires_at, u.username, u.role
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.expires_at > ?
        ORDER BY s.created_at DESC
        LIMIT 1
        """,
        (now_iso,),
    )
    return cur.fetchone()


# -------------------------
# PASSENGERS (stored as JSON in users.passengers TEXT)
# -------------------------
def get_passengers_for_user(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT passengers FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        return None
    # row may be sqlite3.Row -> allow dict-style or index
    try:
        return row["passengers"]
    except Exception:
        return row[0]


def save_passengers_for_user(conn, user_id, passengers_json):
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET passengers = ? WHERE id = ?", (passengers_json, user_id)
    )
    conn.commit()


# -------------------------
# BOOKING QUERIES
# -------------------------


def create_booking(
    conn,
    booking_code,
    user_id,
    train_id,
    origin_station_id,
    destination_station_id,
    travel_date,
    fare,
):
    """
    Insert a new booking record.

    Returns the new booking id.
    """
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bookings (
            booking_code,
            user_id,
            train_id,
            origin_station_id,
            destination_station_id,
            travel_date,
            fare
        )
        VALUES (?, ?, ?, ?, ?, ?,?)
        """,
        (
            booking_code,
            user_id,
            train_id,
            origin_station_id,
            destination_station_id,
            travel_date,
            fare,
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_bookings_by_user(conn, user_id):
    """
    Return all bookings for a user with train, station & payment details.

    - Includes pending bookings (no payment yet)
    - Includes confirmed bookings with payment info
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            b.id,
            b.booking_code,
            b.travel_date,
            b.fare,
            b.status AS booking_status,
            b.created_at,

            t.train_number,
            t.train_name,

            so.name AS origin_station,
            sd.name AS destination_station,

            p.amount AS payment_amount,
            p.method AS payment_method,
            p.status AS payment_status,
            p.transaction_id

        FROM bookings b
        JOIN trains t ON b.train_id = t.id
        JOIN stations so ON b.origin_station_id = so.id
        JOIN stations sd ON b.destination_station_id = sd.id
        LEFT JOIN payments p ON p.booking_id = b.id

        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
        """,
        (user_id,),
    )
    return cur.fetchall()


def get_booking_by_code(conn, booking_code):
    """
    Fetch a single booking using booking_code.
    """
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM bookings
        WHERE booking_code = ?
        """,
        (booking_code,),
    )
    return cur.fetchone()


def cancel_booking(conn, booking_code):
    """
    Mark a booking as cancelled.
    """
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE bookings
        SET status = 'cancelled'
        WHERE booking_code = ?
        """,
        (booking_code,),
    )
    conn.commit()
