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

def create_user(conn, username, email, password_hash, role):
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (username, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """,
        (username, email, password_hash, role)
    )
    conn.commit()
    return cursor.lastrowid


def get_user_by_username(conn, username):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    return cursor.fetchone()


def get_user_by_email(conn, email):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )
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
            travel_date
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            train_id,
            origin_station_id,
            destination_station_id,
            departure_time,
            arrival_time,
            travel_date,
        ),
    )
    conn.commit()
    return cur.lastrowid


def find_schedules(conn, origin_id, destination_id, travel_date):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT s.*, t.train_number, t.train_name
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
