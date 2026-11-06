-- ============================================================================
-- RAILWAY RESERVATION SYSTEM (DBMS COURSE PROJECT)
-- File: sql/schema.sql
-- Description: DDL definitions, integrity constraints, indexes, triggers, and
--              the mandatory VIEW adhering to professor's reference topics.
-- ============================================================================

-- Drop views, triggers, and tables in reverse dependency order
DROP VIEW IF EXISTS v_train_occupancy_summary CASCADE;
DROP TRIGGER IF EXISTS trg_booking_cancellation ON bookings CASCADE;
DROP FUNCTION IF EXISTS log_booking_cancellation CASCADE;
DROP TABLE IF EXISTS booking_cancellation_logs CASCADE;
DROP TABLE IF EXISTS booking_passengers CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS train_class_capacity CASCADE;
DROP TABLE IF EXISTS travel_classes CASCADE;
DROP TABLE IF EXISTS train_runs CASCADE;
DROP TABLE IF EXISTS train_stops CASCADE;
DROP TABLE IF EXISTS trains CASCADE;
DROP TABLE IF EXISTS stations CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ----------------------------------------------------------------------------
-- 1. USERS (Regular Entity - Step 1 of ER-to-Relational Mapping)
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id          SERIAL PRIMARY KEY,
    email            VARCHAR(120) NOT NULL,
    password_hash    VARCHAR(255) NOT NULL,
    full_name        VARCHAR(100) NOT NULL,
    phone            VARCHAR(15)  NOT NULL,
    role             VARCHAR(20)  NOT NULL DEFAULT 'PASSENGER',
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_role CHECK (role IN ('PASSENGER', 'ADMIN'))
);

-- ----------------------------------------------------------------------------
-- 2. STATIONS (Regular Entity - Step 1)
-- ----------------------------------------------------------------------------
CREATE TABLE stations (
    station_code     VARCHAR(10)  PRIMARY KEY,
    station_name     VARCHAR(100) NOT NULL,
    city             VARCHAR(60)  NOT NULL,
    state            VARCHAR(60)  NOT NULL
);

-- ----------------------------------------------------------------------------
-- 3. TRAINS (Regular Entity with 1:N foreign keys to Stations - Steps 1 & 4)
-- ----------------------------------------------------------------------------
CREATE TABLE trains (
    train_number              VARCHAR(10)  PRIMARY KEY,
    train_name                VARCHAR(100) NOT NULL,
    source_station_code       VARCHAR(10)  NOT NULL,
    destination_station_code  VARCHAR(10)  NOT NULL,
    CONSTRAINT fk_trains_source FOREIGN KEY (source_station_code)
        REFERENCES stations(station_code) ON UPDATE CASCADE,
    CONSTRAINT fk_trains_destination FOREIGN KEY (destination_station_code)
        REFERENCES stations(station_code) ON UPDATE CASCADE,
    CONSTRAINT chk_train_endpoints CHECK (source_station_code <> destination_station_code)
);

-- ----------------------------------------------------------------------------
-- 4. TRAIN_STOPS (Weak Entity owned by TRAINS - Step 2)
--    Identifying owner: trains(train_number)
--    Partial key: stop_sequence
--    Composite primary key: (train_number, stop_sequence)
-- ----------------------------------------------------------------------------
CREATE TABLE train_stops (
    train_number              VARCHAR(10)  NOT NULL,
    stop_sequence             INT          NOT NULL,
    station_code              VARCHAR(10)  NOT NULL,
    arrival_time              TIME,
    departure_time            TIME,
    halt_minutes              INT          NOT NULL DEFAULT 2,
    distance_km               INT          NOT NULL DEFAULT 0,
    PRIMARY KEY (train_number, stop_sequence),
    CONSTRAINT fk_stops_train FOREIGN KEY (train_number)
        REFERENCES trains(train_number) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_stops_station FOREIGN KEY (station_code)
        REFERENCES stations(station_code) ON UPDATE CASCADE,
    CONSTRAINT chk_stops_sequence CHECK (stop_sequence > 0),
    CONSTRAINT chk_stops_halt CHECK (halt_minutes >= 0),
    CONSTRAINT chk_stops_distance CHECK (distance_km >= 0),
    CONSTRAINT uq_train_station UNIQUE (train_number, station_code)
);

-- ----------------------------------------------------------------------------
-- 5. TRAIN_RUNS (Scheduled instances of a Train - Step 1 & Step 4)
-- ----------------------------------------------------------------------------
CREATE TABLE train_runs (
    run_id           SERIAL       PRIMARY KEY,
    train_number     VARCHAR(10)  NOT NULL,
    journey_date     DATE         NOT NULL,
    status           VARCHAR(20)  NOT NULL DEFAULT 'SCHEDULED',
    CONSTRAINT fk_runs_train FOREIGN KEY (train_number)
        REFERENCES trains(train_number) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT uq_train_run UNIQUE (train_number, journey_date),
    CONSTRAINT chk_runs_status CHECK (status IN ('SCHEDULED', 'CANCELLED', 'COMPLETED'))
);

-- ----------------------------------------------------------------------------
-- 6. TRAVEL_CLASSES (Regular Entity - Step 1)
-- ----------------------------------------------------------------------------
CREATE TABLE travel_classes (
    class_code       VARCHAR(10) PRIMARY KEY,
    class_name       VARCHAR(50) NOT NULL
);

-- ----------------------------------------------------------------------------
-- 7. TRAIN_CLASS_CAPACITY (M:N Relationship between Runs and Classes - Step 5)
-- ----------------------------------------------------------------------------
CREATE TABLE train_class_capacity (
    run_id           INT            NOT NULL,
    class_code       VARCHAR(10)    NOT NULL,
    total_capacity   INT            NOT NULL,
    base_fare        NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (run_id, class_code),
    CONSTRAINT fk_cap_run FOREIGN KEY (run_id)
        REFERENCES train_runs(run_id) ON DELETE CASCADE,
    CONSTRAINT fk_cap_class FOREIGN KEY (class_code)
        REFERENCES travel_classes(class_code) ON UPDATE CASCADE,
    CONSTRAINT chk_cap_total CHECK (total_capacity > 0),
    CONSTRAINT chk_cap_fare CHECK (base_fare >= 0)
);

-- ----------------------------------------------------------------------------
-- 8. BOOKINGS (Regular Entity with multiple 1:N relationships - Step 1 & Step 4)
-- ----------------------------------------------------------------------------
CREATE TABLE bookings (
    booking_id          SERIAL         PRIMARY KEY,
    pnr                 VARCHAR(10)    NOT NULL,
    user_id             INT            NOT NULL,
    run_id              INT            NOT NULL,
    from_station_code   VARCHAR(10)    NOT NULL,
    to_station_code     VARCHAR(10)    NOT NULL,
    class_code          VARCHAR(10)    NOT NULL,
    booking_date        TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_fare          NUMERIC(10, 2) NOT NULL,
    booking_status      VARCHAR(20)    NOT NULL DEFAULT 'CONFIRMED',
    CONSTRAINT uq_bookings_pnr UNIQUE (pnr),
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_run FOREIGN KEY (run_id)
        REFERENCES train_runs(run_id) ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_from_stn FOREIGN KEY (from_station_code)
        REFERENCES stations(station_code),
    CONSTRAINT fk_bookings_to_stn FOREIGN KEY (to_station_code)
        REFERENCES stations(station_code),
    CONSTRAINT fk_bookings_class FOREIGN KEY (class_code)
        REFERENCES travel_classes(class_code),
    CONSTRAINT chk_bookings_status CHECK (booking_status IN ('CONFIRMED', 'CANCELLED')),
    CONSTRAINT chk_bookings_stations CHECK (from_station_code <> to_station_code),
    CONSTRAINT chk_bookings_fare CHECK (total_fare >= 0)
);

-- ----------------------------------------------------------------------------
-- 9. BOOKING_PASSENGERS (Weak Entity owned by BOOKINGS - Step 2)
--    Identifying owner: bookings(booking_id)
--    Partial key: passenger_seq
--    Composite primary key: (booking_id, passenger_seq)
-- ----------------------------------------------------------------------------
CREATE TABLE booking_passengers (
    booking_id       INT          NOT NULL,
    passenger_seq    INT          NOT NULL,
    passenger_name   VARCHAR(100) NOT NULL,
    age              INT          NOT NULL,
    gender           VARCHAR(10)  NOT NULL,
    PRIMARY KEY (booking_id, passenger_seq),
    CONSTRAINT fk_passengers_booking FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id) ON DELETE CASCADE,
    CONSTRAINT chk_passengers_seq CHECK (passenger_seq BETWEEN 1 AND 6),
    CONSTRAINT chk_passengers_age CHECK (age BETWEEN 1 AND 120),
    CONSTRAINT chk_passengers_gender CHECK (gender IN ('MALE', 'FEMALE', 'OTHER'))
);

-- ----------------------------------------------------------------------------
-- 10. BOOKING_CANCELLATION_LOGS (Audit table populated via Trigger)
-- ----------------------------------------------------------------------------
CREATE TABLE booking_cancellation_logs (
    log_id              SERIAL       PRIMARY KEY,
    booking_id          INT          NOT NULL,
    pnr                 VARCHAR(10)  NOT NULL,
    cancelled_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancellation_reason VARCHAR(255) NOT NULL DEFAULT 'User requested online cancellation'
);

-- ----------------------------------------------------------------------------
-- MANDATORY SQL VIEW: v_train_occupancy_summary
-- Hides complex multi-table joins and aggregation for Viva / App reporting
-- ----------------------------------------------------------------------------
CREATE VIEW v_train_occupancy_summary AS
SELECT
    tr.run_id,
    t.train_number,
    t.train_name,
    tr.journey_date,
    tr.status AS run_status,
    tc.class_code,
    cl.class_name,
    tc.total_capacity,
    tc.base_fare,
    COALESCE(COUNT(bp.passenger_seq), 0)::INT AS booked_seats,
    (tc.total_capacity - COALESCE(COUNT(bp.passenger_seq), 0))::INT AS available_seats
FROM train_runs tr
JOIN trains t ON tr.train_number = t.train_number
JOIN train_class_capacity tc ON tr.run_id = tc.run_id
JOIN travel_classes cl ON tc.class_code = cl.class_code
LEFT JOIN bookings b ON b.run_id = tr.run_id
    AND b.class_code = tc.class_code
    AND b.booking_status = 'CONFIRMED'
LEFT JOIN booking_passengers bp ON b.booking_id = bp.booking_id
GROUP BY
    tr.run_id,
    t.train_number,
    t.train_name,
    tr.journey_date,
    tr.status,
    tc.class_code,
    cl.class_name,
    tc.total_capacity,
    tc.base_fare;

-- ----------------------------------------------------------------------------
-- OPTIONAL TRIGGER: Logs cancellations into audit table (SQL Slide 236)
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION log_booking_cancellation()
RETURNS TRIGGER AS $$
BEGIN
    IF (OLD.booking_status = 'CONFIRMED' AND NEW.booking_status = 'CANCELLED') THEN
        INSERT INTO booking_cancellation_logs (booking_id, pnr, cancelled_at, cancellation_reason)
        VALUES (NEW.booking_id, NEW.pnr, CURRENT_TIMESTAMP, 'Cancellation status updated to CANCELLED');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_booking_cancellation
AFTER UPDATE OF booking_status ON bookings
FOR EACH ROW
EXECUTE FUNCTION log_booking_cancellation();

-- Helpful Indexes for Foreign Keys & Search Performance
CREATE INDEX idx_train_stops_train ON train_stops(train_number);
CREATE INDEX idx_train_stops_station ON train_stops(station_code);
CREATE INDEX idx_train_runs_date ON train_runs(journey_date);
CREATE INDEX idx_bookings_user ON bookings(user_id);
CREATE INDEX idx_bookings_pnr ON bookings(pnr);
CREATE INDEX idx_bookings_run_class ON bookings(run_id, class_code);
