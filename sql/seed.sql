-- ============================================================================
-- RAILWAY RESERVATION SYSTEM (DBMS COURSE PROJECT)
-- File: sql/seed.sql
-- Description: Repeatable realistic fictional demonstration data for Indian Railways.
--              Expanded network covering all 12 stations and multi-month calendar runs.
-- ============================================================================

-- Clean existing data in reverse dependency order
TRUNCATE TABLE booking_cancellation_logs CASCADE;
TRUNCATE TABLE booking_passengers CASCADE;
TRUNCATE TABLE bookings CASCADE;
TRUNCATE TABLE train_class_capacity CASCADE;
TRUNCATE TABLE travel_classes CASCADE;
TRUNCATE TABLE train_runs CASCADE;
TRUNCATE TABLE train_stops CASCADE;
TRUNCATE TABLE trains CASCADE;
TRUNCATE TABLE stations CASCADE;
TRUNCATE TABLE users CASCADE;

-- ----------------------------------------------------------------------------
-- 1. USERS
-- ----------------------------------------------------------------------------
INSERT INTO users (user_id, email, password_hash, full_name, phone, role) VALUES
(1, 'admin@railway.com', 'scrypt:32768:8:1$K4INLIzc4K8fdg8O$d62d96c88c5c9e1e1cbb2b6d72ce37bbbee2e4aa5a07e9271301373093d389752caa9fcfb4f1f8d2047620910a4737f6618413399ac6fad3577c459021aa09a1', 'Railway Administrator', '9876543210', 'ADMIN'),
(2, 'passenger@railway.com', 'scrypt:32768:8:1$cITJPO3NY4mrL8vV$73987f1334d4ce6fb111c28d5eb63aebe213d856c91954cde480234cd8a44b975c1bf09578071cb10a3aefe5c9e24d5d7c52c8f9f54991a88c5a9c35bde4c339', 'Suresh Kumar', '9811223344', 'PASSENGER'),
(3, 'rahul@gmail.com', 'scrypt:32768:8:1$RmIBNRaDMD5aRvR1$7f430d9fd70bee1768d7bb8a03ac4d8775e58e265102475043be0ef72122bb8bb12cde91503a1b60a6b80691c5fd1017281b3a68840c903d1a3bcd621dbd539c', 'Rahul Sharma', '9871122334', 'PASSENGER'),
(4, 'priya@gmail.com', 'scrypt:32768:8:1$8o3Y444sWtUyoxMC$b472bc4b0327e48ff862340be79b056c5689bf0a127dce227f296a679bb51070f9410641002a971049572f50233f65c52e1b3ee802d7c795bc7b5d69308a4acf', 'Priya Singh', '9899112233', 'PASSENGER');

SELECT setval('users_user_id_seq', (SELECT MAX(user_id) FROM users));

-- ----------------------------------------------------------------------------
-- 2. STATIONS
-- ----------------------------------------------------------------------------
INSERT INTO stations (station_code, station_name, city, state) VALUES
('NDLS', 'New Delhi Railway Station', 'New Delhi', 'Delhi'),
('CNB',  'Kanpur Central', 'Kanpur', 'Uttar Pradesh'),
('PRYJ', 'Prayagraj Junction', 'Prayagraj', 'Uttar Pradesh'),
('DDU',  'Pt. Deen Dayal Upadhyaya Junction', 'Mughalsarai', 'Uttar Pradesh'),
('PNBE', 'Patna Junction', 'Patna', 'Bihar'),
('HWH',  'Howrah Junction', 'Kolkata', 'West Bengal'),
('BCT',  'Mumbai Central', 'Mumbai', 'Maharashtra'),
('BRC',  'Vadodara Junction', 'Vadodara', 'Gujarat'),
('ST',   'Surat Railway Station', 'Surat', 'Gujarat'),
('ADI',  'Ahmedabad Junction', 'Ahmedabad', 'Gujarat'),
('MAS',  'Chennai Central', 'Chennai', 'Tamil Nadu'),
('SBC',  'KSR Bengaluru City', 'Bengaluru', 'Karnataka');

-- ----------------------------------------------------------------------------
-- 3. TRAINS (Full Network Interconnecting All 12 Stations)
-- ----------------------------------------------------------------------------
INSERT INTO trains (train_number, train_name, source_station_code, destination_station_code) VALUES
('12302', 'Howrah Rajdhani Express', 'NDLS', 'HWH'),
('12301', 'New Delhi Rajdhani Express', 'HWH', 'NDLS'),
('12394', 'Sampoorna Kranti Express', 'NDLS', 'PNBE'),
('12393', 'Sampoorna Kranti Express', 'PNBE', 'NDLS'),
('12952', 'Mumbai Rajdhani Express', 'NDLS', 'BCT'),
('12951', 'Mumbai Rajdhani Express', 'BCT', 'NDLS'),
('12004', 'Lucknow Swarna Shatabdi', 'NDLS', 'CNB'),
('12003', 'Lucknow Swarna Shatabdi', 'CNB', 'NDLS'),
('12626', 'Kerala Express', 'NDLS', 'MAS'),
('12625', 'Kerala Express', 'MAS', 'NDLS'),
('12296', 'Sanghamitra Express', 'SBC', 'PNBE'),
('12295', 'Sanghamitra Express', 'PNBE', 'SBC'),
('12650', 'Karnataka Sampark Kranti', 'NDLS', 'SBC'),
('12649', 'Karnataka Sampark Kranti', 'SBC', 'NDLS'),
('12834', 'Howrah Ahmedabad Express', 'HWH', 'ADI'),
('12833', 'Ahmedabad Howrah Express', 'ADI', 'HWH');

-- ----------------------------------------------------------------------------
-- 4. TRAIN_STOPS (Ordered Route Sequences)
-- ----------------------------------------------------------------------------
-- 12302: NDLS -> CNB -> PRYJ -> DDU -> HWH
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12302', 1, 'NDLS', NULL, '16:50:00', 0, 0),
('12302', 2, 'CNB',  '21:32:00', '21:37:00', 5, 440),
('12302', 3, 'PRYJ', '23:43:00', '23:45:00', 2, 635),
('12302', 4, 'DDU',  '01:37:00', '01:47:00', 10, 786),
('12302', 5, 'HWH',  '09:55:00', NULL, 0, 1445);

-- 12301: HWH -> DDU -> PRYJ -> CNB -> NDLS
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12301', 1, 'HWH',  NULL, '16:50:00', 0, 0),
('12301', 2, 'DDU',  '00:45:00', '00:55:00', 10, 659),
('12301', 3, 'PRYJ', '02:43:00', '02:45:00', 2, 810),
('12301', 4, 'CNB',  '04:50:00', '04:55:00', 5, 1005),
('12301', 5, 'NDLS', '10:05:00', NULL, 0, 1445);

-- 12394: NDLS -> CNB -> DDU -> PNBE
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12394', 1, 'NDLS', NULL, '17:30:00', 0, 0),
('12394', 2, 'CNB',  '22:22:00', '22:30:00', 8, 440),
('12394', 3, 'DDU',  '02:25:00', '02:35:00', 10, 786),
('12394', 4, 'PNBE', '06:50:00', NULL, 0, 998);

-- 12393: PNBE -> DDU -> CNB -> NDLS
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12393', 1, 'PNBE', NULL, '19:25:00', 0, 0),
('12393', 2, 'DDU',  '22:20:00', '22:30:00', 10, 212),
('12393', 3, 'CNB',  '02:25:00', '02:30:00', 5, 558),
('12393', 4, 'NDLS', '07:55:00', NULL, 0, 998);

-- 12952: NDLS -> BRC -> ST -> BCT
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12952', 1, 'NDLS', NULL, '16:55:00', 0, 0),
('12952', 2, 'BRC',  '03:20:00', '03:30:00', 10, 992),
('12952', 3, 'ST',   '05:10:00', '05:15:00', 5, 1122),
('12952', 4, 'BCT',  '08:35:00', NULL, 0, 1384);

-- 12951: BCT -> ST -> BRC -> NDLS
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12951', 1, 'BCT',  NULL, '17:00:00', 0, 0),
('12951', 2, 'ST',   '19:43:00', '19:48:00', 5, 262),
('12951', 3, 'BRC',  '21:06:00', '21:16:00', 10, 392),
('12951', 4, 'NDLS', '08:32:00', NULL, 0, 1384);

-- 12004: NDLS -> CNB
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12004', 1, 'NDLS', NULL, '06:10:00', 0, 0),
('12004', 2, 'CNB',  '11:20:00', NULL, 0, 440);

-- 12003: CNB -> NDLS
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12003', 1, 'CNB',  NULL, '16:50:00', 0, 0),
('12003', 2, 'NDLS', '22:05:00', NULL, 0, 440);

-- 12626: NDLS -> CNB -> MAS
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12626', 1, 'NDLS', NULL, '20:10:00', 0, 0),
('12626', 2, 'CNB',  '02:20:00', '02:30:00', 10, 440),
('12626', 3, 'MAS',  '04:30:00', NULL, 0, 2180);

-- 12625: MAS -> CNB -> NDLS
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12625', 1, 'MAS',  NULL, '06:15:00', 0, 0),
('12625', 2, 'CNB',  '08:20:00', '08:30:00', 10, 1740),
('12625', 3, 'NDLS', '14:40:00', NULL, 0, 2180);

-- 12296: Sanghamitra Express: SBC -> MAS -> PRYJ -> DDU -> PNBE
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12296', 1, 'SBC',  NULL, '09:00:00', 0, 0),
('12296', 2, 'MAS',  '13:50:00', '14:15:00', 25, 362),
('12296', 3, 'PRYJ', '16:05:00', '16:15:00', 10, 2060),
('12296', 4, 'DDU',  '18:40:00', '18:50:00', 10, 2212),
('12296', 5, 'PNBE', '23:15:00', NULL, 0, 2424);

-- 12295: Sanghamitra Express: PNBE -> DDU -> PRYJ -> MAS -> SBC
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12295', 1, 'PNBE', NULL, '20:15:00', 0, 0),
('12295', 2, 'DDU',  '23:45:00', '23:55:00', 10, 212),
('12295', 3, 'PRYJ', '01:50:00', '02:00:00', 10, 364),
('12295', 4, 'MAS',  '03:15:00', '03:40:00', 25, 2062),
('12295', 5, 'SBC',  '09:20:00', NULL, 0, 2424);

-- 12650: Karnataka Sampark Kranti: NDLS -> CNB -> SBC
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12650', 1, 'NDLS', NULL, '06:25:00', 0, 0),
('12650', 2, 'CNB',  '12:00:00', '12:10:00', 10, 440),
('12650', 3, 'SBC',  '19:45:00', NULL, 0, 2400);

-- 12649: Karnataka Sampark Kranti: SBC -> CNB -> NDLS
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12649', 1, 'SBC',  NULL, '06:30:00', 0, 0),
('12649', 2, 'CNB',  '14:15:00', '14:25:00', 10, 1960),
('12649', 3, 'NDLS', '20:10:00', NULL, 0, 2400);

-- 12834: Howrah Ahmedabad Express: HWH -> DDU -> BRC -> ST -> ADI
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12834', 1, 'HWH',  NULL, '23:55:00', 0, 0),
('12834', 2, 'DDU',  '09:40:00', '09:50:00', 10, 659),
('12834', 3, 'BRC',  '08:15:00', '08:25:00', 10, 1950),
('12834', 4, 'ST',   '09:45:00', '09:50:00', 5, 2080),
('12834', 5, 'ADI',  '12:05:00', NULL, 0, 2180);

-- 12833: Ahmedabad Howrah Express: ADI -> ST -> BRC -> DDU -> HWH
INSERT INTO train_stops (train_number, stop_sequence, station_code, arrival_time, departure_time, halt_minutes, distance_km) VALUES
('12833', 1, 'ADI',  NULL, '00:25:00', 0, 0),
('12833', 2, 'ST',   '03:45:00', '03:50:00', 5, 100),
('12833', 3, 'BRC',  '05:10:00', '05:20:00', 10, 230),
('12833', 4, 'DDU',  '03:30:00', '03:40:00', 10, 1521),
('12833', 5, 'HWH',  '13:30:00', NULL, 0, 2180);

-- ----------------------------------------------------------------------------
-- 5. TRAVEL_CLASSES
-- ----------------------------------------------------------------------------
INSERT INTO travel_classes (class_code, class_name) VALUES
('SL',  'Sleeper Class (Non-AC)'),
('3AC', 'AC 3 Tier Sleeper'),
('2AC', 'AC 2 Tier Sleeper'),
('1AC', 'AC First Class');

-- ----------------------------------------------------------------------------
-- 6. Initial Sample Bookings for Demonstration
-- ----------------------------------------------------------------------------
-- Base runs are populated dynamically via python db.py init to cover upcoming 90 days.
