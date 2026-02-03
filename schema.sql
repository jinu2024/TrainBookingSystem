-- Schema for TrainBookingSystem
-- Users table (admins and passengers)
CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL UNIQUE,
	email TEXT NOT NULL UNIQUE,
	password_hash TEXT NOT NULL,
	role TEXT NOT NULL DEFAULT 'passenger',
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- 