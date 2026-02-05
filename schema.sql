-- Schema for TrainBookingSystem
-- USERS
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'customer')) NOT NULL,
    status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- STATIONS
CREATE TABLE IF NOT EXISTS stations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    city TEXT NOT NULL
);

-- TRAINS
CREATE TABLE IF NOT EXISTS trains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_number TEXT NOT NULL UNIQUE,
    train_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active'
);

-- SCHEDULES
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id INTEGER NOT NULL,
    origin_station_id INTEGER NOT NULL,
    destination_station_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    travel_date TEXT NOT NULL,
    FOREIGN KEY (train_id) REFERENCES trains(id),
    FOREIGN KEY (origin_station_id) REFERENCES stations(id),
    FOREIGN KEY (destination_station_id) REFERENCES stations(id)
);

-- BOOKINGS
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    booking_code TEXT NOT NULL UNIQUE,

    user_id INTEGER NOT NULL,
    train_id INTEGER NOT NULL,

    origin_station_id INTEGER NOT NULL,
    destination_station_id INTEGER NOT NULL,

    travel_date TEXT NOT NULL,

    status TEXT CHECK(status IN ('confirmed', 'cancelled')) DEFAULT 'confirmed',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (train_id) REFERENCES trains(id),
    FOREIGN KEY (origin_station_id) REFERENCES stations(id),
    FOREIGN KEY (destination_station_id) REFERENCES stations(id)
);

