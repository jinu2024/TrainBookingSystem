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

INSERT OR IGNORE INTO stations (code, name, city) VALUES
('IND001','Indore Junction','Indore'),
('REW002','Rewa Junction','Rewa'),
('BPL003','Bhopal Junction','Bhopal'),
('DEL004','New Delhi','Delhi'),
('AGR005','Agra Cantt','Agra'),
('GWL006','Gwalior','Gwalior'),
('JBP007','Jabalpur','Jabalpur'),
('NGP008','Nagpur','Nagpur'),
('ITR009','Itarsi','Itarsi'),
('KOTA10','Kota Junction','Kota'),
('JPR011','Jaipur','Jaipur'),
('LKO012','Lucknow','Lucknow'),
('CNB013','Kanpur Central','Kanpur'),
('ALD014','Prayagraj','Allahabad'),
('BSB015','Varanasi','Varanasi'),
('RNC016','Ranchi','Ranchi'),
('HWH017','Howrah','Kolkata'),
('BBS018','Bhubaneswar','Bhubaneswar'),
('MAS019','Chennai Central','Chennai'),
('SBC020','Bangalore City','Bangalore'),
('HYD021','Hyderabad','Hyderabad'),
('PUN022','Pune Junction','Pune'),
('NGP213','Nagpur Junction','Nagpur'),
('KOTA31','Kota Junction','Kota'),
('GWL312','Gwalior Junction','Gwalior'),
('VSKP42','Visakhapatnam','Visakhapatnam'),
('NDLS10','New Delhi','Delhi'),
('JP5754','Jaipur Junction','Jaipur'),
('PUNE43','Pune Junction','Pune'),
('SUR455','Solapur','Solapur'),
('UBL767','Hubballi Junction','Hubballi'),
('MYS435','Mysuru Junction','Mysuru');

-- TRAINS
CREATE TABLE IF NOT EXISTS trains (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_number TEXT NOT NULL UNIQUE,
    train_name TEXT NOT NULL,
    status TEXT CHECK(status IN ('active', 'inactive')) DEFAULT 'active'
);

INSERT OR IGNORE INTO trains (train_number, train_name) VALUES
('12001','Indore Express'),
('12002','Central Bharat Superfast'),
('12003','Ganga Valley Express'),
('12004','Southern Link Express'),
('12005','Deccan Connect');

-- SCHEDULES
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id INTEGER NOT NULL,
    origin_station_id INTEGER NOT NULL,
    destination_station_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    departure_date TEXT NOT NULL,
    arrival_date TEXT NOT NULL,
    fare REAL NOT NULL,
    FOREIGN KEY (train_id) REFERENCES trains(id),
    FOREIGN KEY (origin_station_id) REFERENCES stations(id),
    FOREIGN KEY (destination_station_id) REFERENCES stations(id)
    UNIQUE (
        train_id,
        origin_station_id,
        destination_station_id,
        departure_date,
        departure_time
    )
);

-- 🚄 Train 1 → Indore → Rewa → Bhopal → Delhi → Agra
INSERT OR IGNORE INTO schedules VALUES
(NULL,1,1,2,'06:00','09:30','2026-02-15','2026-02-15',220),
(NULL,1,2,3,'10:00','13:00','2026-02-15','2026-02-15',180),
(NULL,1,3,4,'14:00','18:30','2026-02-15','2026-02-15',300),
(NULL,1,4,5,'19:00','21:00','2026-02-15','2026-02-15',120);

-- 🚄 Train 2 → Delhi → Agra → Gwalior → Bhopal → Nagpur
INSERT OR IGNORE INTO schedules VALUES
(NULL,2,4,5,'07:00','08:45','2026-02-16','2026-02-16',150),
(NULL,2,5,6,'09:10','10:30','2026-02-16','2026-02-16',130),
(NULL,2,6,3,'11:00','14:30','2026-02-16','2026-02-16',260),
(NULL,2,3,8,'15:00','20:00','2026-02-16','2026-02-16',350);

-- 🚄 Train 3 → Lucknow → Kanpur → Prayagraj → Varanasi → Ranchi
INSERT OR IGNORE INTO schedules VALUES
(NULL,3,12,13,'05:30','06:30','2026-02-17','2026-02-17',90),
(NULL,3,13,14,'07:00','09:00','2026-02-17','2026-02-17',140),
(NULL,3,14,15,'09:30','11:00','2026-02-17','2026-02-17',110),
(NULL,3,15,16,'12:00','17:00','2026-02-17','2026-02-17',420);

-- 🚄 Train 4 → Chennai → Bangalore → Hyderabad → Nagpur → Bhopal
INSERT OR IGNORE INTO schedules VALUES
(NULL,4,19,20,'06:00','11:00','2026-02-18','2026-02-18',380),
(NULL,4,20,21,'12:00','17:00','2026-02-18','2026-02-18',400),
(NULL,4,21,8,'18:00','23:00','2026-02-18','2026-02-18',350),
(NULL,4,8,3,'23:30','05:00','2026-02-19','2026-02-19',420);

-- 🚄 Train 5 → Pune → Itarsi → Jabalpur → Varanasi → Howrah
INSERT OR IGNORE INTO schedules VALUES
(NULL,5,22,9,'05:00','10:00','2026-02-20','2026-02-20',300),
(NULL,5,9,7,'10:30','14:00','2026-02-20','2026-02-20',210),
(NULL,5,7,15,'14:30','19:30','2026-02-20','2026-02-20',350),
(NULL,5,15,17,'20:00','06:00','2026-02-21','2026-02-21',600);

-- 🚆 Train 6 – Malwa Express (Indore → Rewa → Bhopal → Jabalpur → Prayagraj)
INSERT OR IGNORE INTO schedules VALUES
(NULL,1,(SELECT id FROM stations WHERE code='IND001'),(SELECT id FROM stations WHERE code='REW002'),'06:00','10:30','2026-02-12','2026-02-12',250),
(NULL,1,(SELECT id FROM stations WHERE code='REW002'),(SELECT id FROM stations WHERE code='BPL003'),'11:00','15:30','2026-02-12','2026-02-12',200),
(NULL,1,(SELECT id FROM stations WHERE code='BPL003'),(SELECT id FROM stations WHERE code='JBP007'),'16:00','20:00','2026-02-12','2026-02-12',180),
(NULL,1,(SELECT id FROM stations WHERE code='JBP007'),(SELECT id FROM stations WHERE code='ALD014'),'20:30','03:30','2026-02-12','2026-02-13',350);

-- 🚆 Train 7 – MP Superfast (Indore → Ujjain → Kota → Jaipur → Delhi)
INSERT OR IGNORE INTO schedules VALUES
(NULL,2,(SELECT id FROM stations WHERE code='IND001'),(SELECT id FROM stations WHERE code='ITR009'),'05:00','06:30','2026-02-12','2026-02-12',90),
(NULL,2,(SELECT id FROM stations WHERE code='ITR009'),(SELECT id FROM stations WHERE code='KOTA10'),'07:00','10:30','2026-02-12','2026-02-12',150),
(NULL,2,(SELECT id FROM stations WHERE code='KOTA10'),(SELECT id FROM stations WHERE code='JPR011'),'11:00','14:00','2026-02-12','2026-02-12',170),
(NULL,2,(SELECT id FROM stations WHERE code='JPR011'),(SELECT id FROM stations WHERE code='DEL004'),'14:30','19:00','2026-02-12','2026-02-12',300);

-- 🚆 Train 8 – Central India Express (Bhopal → Nagpur → Visakhapatnam)
INSERT OR IGNORE INTO schedules VALUES
(NULL,3,(SELECT id FROM stations WHERE code='BPL003'),(SELECT id FROM stations WHERE code='NGP008'),'07:00','13:00','2026-02-12','2026-02-12',400),
(NULL,3,(SELECT id FROM stations WHERE code='NGP008'),(SELECT id FROM stations WHERE code='VSKP42'),'13:30','23:30','2026-02-12','2026-02-12',600);

-- 🚆 Train 9 – South Connect (Pune → Solapur → Hubballi → Mysuru)
INSERT OR IGNORE INTO schedules VALUES
(NULL,4,(SELECT id FROM stations WHERE code='PUN022'),(SELECT id FROM stations WHERE code='SUR455'),'06:00','09:30','2026-02-12','2026-02-12',220),
(NULL,4,(SELECT id FROM stations WHERE code='SUR455'),(SELECT id FROM stations WHERE code='UBL767'),'10:00','14:00','2026-02-12','2026-02-12',240),
(NULL,4,(SELECT id FROM stations WHERE code='UBL767'),(SELECT id FROM stations WHERE code='MYS435'),'14:30','20:00','2026-02-12','2026-02-12',300);

-- 🚆 Train 10 – North MP Passenger (Gwalior → Bhopal → Indore → Ujjain → Kota)
INSERT OR IGNORE INTO schedules VALUES
(NULL,5,(SELECT id FROM stations WHERE code='GWL006'),(SELECT id FROM stations WHERE code='BPL003'),'05:30','09:30','2026-02-12','2026-02-12',180),
(NULL,5,(SELECT id FROM stations WHERE code='BPL003'),(SELECT id FROM stations WHERE code='IND001'),'10:00','13:00','2026-02-12','2026-02-12',160),
(NULL,5,(SELECT id FROM stations WHERE code='IND001'),(SELECT id FROM stations WHERE code='ITR009'),'13:20','14:30','2026-02-12','2026-02-12',80),
(NULL,5,(SELECT id FROM stations WHERE code='ITR009'),(SELECT id FROM stations WHERE code='KOTA10'),'15:00','19:00','2026-02-12','2026-02-12',170);

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


