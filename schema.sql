-- Schema for TrainBookingSystem
-- USERS
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    mobile TEXT,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('admin', 'customer')) NOT NULL,
    status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active',
    full_name TEXT,
    dob TEXT,
    gender TEXT,
    aadhaar TEXT,
    nationality TEXT,
    address TEXT,
    passengers TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email),
    UNIQUE(mobile),
    UNIQUE(aadhaar)
);

-- Auto add admin user
INSERT OR IGNORE INTO users (username, email, mobile, password_hash, role, full_name, dob) VALUES
('admin', 'admin@tcs.com', '9876543210', '7676aaafb027c825bd9abab78b234070e702752f625b752e55e55b48e607e358', 'admin', 'Admin User', '1990-01-01');

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
    fare REAL NOT NULL,
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
    fare REAL NOT NULL,

    status TEXT CHECK(status IN ('confirmed', 'cancelled')) DEFAULT 'confirmed',

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (train_id) REFERENCES trains(id),
    FOREIGN KEY (origin_station_id) REFERENCES stations(id),
    FOREIGN KEY (destination_station_id) REFERENCES stations(id)
);

-- SESSIONS
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);


-- PAYMENTS
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    booking_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    method TEXT CHECK(method IN ('upi', 'card', 'netbanking')) NOT NULL,

    status TEXT CHECK(status IN ('success', 'failed', 'pending', 'refunded')) NOT NULL,
    transaction_id TEXT UNIQUE,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (booking_id) REFERENCES bookings(id)
);



