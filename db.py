"""
Database connection and utility module for Railway Reservation System.
Primary Driver: PostgreSQL via psycopg 3 (executing direct parameterized SQL, NO ORM).
Local Fallback Driver: SQLite adapter for instant local zero-dependency testing.
"""

import os
import sys
import re
from datetime import date, datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///d:/dbms_project/railway_dev.db"

FORCE_SQLITE = os.environ.get("USE_SQLITE", "false").lower() in ("true", "1", "yes")

_db_engine = None  # 'postgres' or 'sqlite'

class SQLiteCursorWrapper:
    """
    Wraps an sqlite3.Cursor to provide a psycopg-compatible dictionary-row interface
    and translate PostgreSQL parameter placeholders (%s -> ?).
    """
    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.cursor.close()
        except Exception:
            pass

    def execute(self, query, params=None):
        q = query.replace("%s", "?")
        q = re.sub(r"\bFOR\s+UPDATE\b", "", q, flags=re.IGNORECASE)
        q = re.sub(r"::INT(EGER)?", "", q, flags=re.IGNORECASE)
        q = re.sub(r"CURRENT_DATE\s*\+\s*INTERVAL\s*'(\d+)\s*day[s]?'", r"date('now', '+\1 day')", q, flags=re.IGNORECASE)
        q = re.sub(r"CURRENT_TIMESTAMP\s*-\s*INTERVAL\s*'(\d+)\s*hour[s]?'", r"datetime('now', '-\1 hours')", q, flags=re.IGNORECASE)
        q = re.sub(r"CURRENT_TIMESTAMP\s*-\s*INTERVAL\s*'(\d+)\s*day[s]?'", r"datetime('now', '-\1 days')", q, flags=re.IGNORECASE)

        if params:
            sanitized_params = []
            for p in params:
                if isinstance(p, (date, datetime)):
                    sanitized_params.append(p.isoformat())
                else:
                    sanitized_params.append(p)
            return self.cursor.execute(q, sanitized_params)
        return self.cursor.execute(q)

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(r) for r in rows]

    def __iter__(self):
        for r in self.cursor:
            yield dict(r)

    @property
    def rowcount(self):
        return self.cursor.rowcount

class SQLiteConnectionWrapper:
    """
    Wraps an sqlite3.Connection with context manager support matching psycopg.
    """
    def __init__(self, conn, autocommit=False):
        self.conn = conn
        self.autocommit = autocommit

    def cursor(self):
        return SQLiteCursorWrapper(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            if self.autocommit:
                self.commit()
        self.close()

def _get_sqlite_connection(autocommit=False):
    import sqlite3
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "railway_dev.db")
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return SQLiteConnectionWrapper(conn, autocommit=autocommit)

def get_connection(autocommit=False):
    """
    Returns a database connection.
    Uses SQLite directly if configured in DATABASE_URL or falling back;
    otherwise connects to PostgreSQL via psycopg.
    """
    global _db_engine

    if FORCE_SQLITE or _db_engine == "sqlite" or DATABASE_URL.startswith("sqlite"):
        _db_engine = "sqlite"
        return _get_sqlite_connection(autocommit=autocommit)

    # Try connecting to PostgreSQL via psycopg with 2-second timeout
    try:
        import psycopg
        from psycopg.rows import dict_row
        conn = psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
            autocommit=autocommit,
            connect_timeout=2
        )
        if _db_engine != "postgres":
            print(f"[DATABASE] Connected successfully to PostgreSQL at: {DATABASE_URL}")
            _db_engine = "postgres"
        return conn
    except Exception as exc:
        if _db_engine != "sqlite":
            print(f"[DATABASE NOTICE] PostgreSQL unreachable ({exc}). Falling back to local SQLite (railway_dev.db).")
            print("[DATABASE NOTICE] Set DATABASE_URL in .env to connect to real PostgreSQL when ready.")
            _db_engine = "sqlite"
            init_sqlite_if_needed()
        return _get_sqlite_connection(autocommit=autocommit)

def init_sqlite_if_needed():
    """Initializes local SQLite database with initial schema and seed data if not yet created."""
    db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "railway_dev.db")
    if not os.path.exists(db_file) or os.path.getsize(db_file) == 0:
        print("[DATABASE INIT] Auto-initializing local SQLite database...")
        init_database(engine="sqlite")

def init_database(seed=True, engine=None):
    """
    Executes DDL schema and seed data on the target database engine.
    Seeds full 12-station network and schedules runs for the next 90 days.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(base_dir, "sql", "schema.sql")
    seed_path = os.path.join(base_dir, "sql", "seed.sql")

    target_engine = engine or _db_engine or ("sqlite" if FORCE_SQLITE or DATABASE_URL.startswith("sqlite") else "postgres")

    if target_engine == "postgres":
        import psycopg
        print(f"[DB INIT] Connecting to PostgreSQL at: {DATABASE_URL}")
        with psycopg.connect(DATABASE_URL, autocommit=False) as conn:
            with conn.cursor() as cur:
                print(f"[DB INIT] Executing {schema_path}...")
                with open(schema_path, "r", encoding="utf-8") as f:
                    cur.execute(f.read())
                if seed and os.path.exists(seed_path):
                    print(f"[DB INIT] Executing {seed_path}...")
                    with open(seed_path, "r", encoding="utf-8") as f:
                        cur.execute(f.read())
                    _seed_calendar_and_demo_data(cur, is_postgres=True)
            conn.commit()
        print("[DB INIT] PostgreSQL initialization complete!")
    else:
        # SQLite Initialization
        import sqlite3
        db_file = os.path.join(base_dir, "railway_dev.db")
        print(f"[DB INIT] Creating local SQLite database at: {db_file}")
        if os.path.exists(db_file):
            try:
                os.remove(db_file)
            except Exception:
                pass

        conn = sqlite3.connect(db_file)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = OFF;")

        # Create tables
        cur.executescript("""
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'PASSENGER' CHECK (role IN ('PASSENGER', 'ADMIN')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE stations (
            station_code TEXT PRIMARY KEY,
            station_name TEXT NOT NULL,
            city TEXT NOT NULL,
            state TEXT NOT NULL
        );

        CREATE TABLE trains (
            train_number TEXT PRIMARY KEY,
            train_name TEXT NOT NULL,
            source_station_code TEXT NOT NULL REFERENCES stations(station_code),
            destination_station_code TEXT NOT NULL REFERENCES stations(station_code)
        );

        CREATE TABLE train_stops (
            train_number TEXT NOT NULL REFERENCES trains(train_number) ON DELETE CASCADE,
            stop_sequence INTEGER NOT NULL,
            station_code TEXT NOT NULL REFERENCES stations(station_code),
            arrival_time TEXT,
            departure_time TEXT,
            halt_minutes INTEGER DEFAULT 2,
            distance_km INTEGER DEFAULT 0,
            PRIMARY KEY (train_number, stop_sequence),
            UNIQUE (train_number, station_code)
        );

        CREATE TABLE train_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            train_number TEXT NOT NULL REFERENCES trains(train_number) ON DELETE CASCADE,
            journey_date DATE NOT NULL,
            status TEXT NOT NULL DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'CANCELLED', 'COMPLETED')),
            UNIQUE (train_number, journey_date)
        );

        CREATE TABLE travel_classes (
            class_code TEXT PRIMARY KEY,
            class_name TEXT NOT NULL
        );

        CREATE TABLE train_class_capacity (
            run_id INTEGER NOT NULL REFERENCES train_runs(run_id) ON DELETE CASCADE,
            class_code TEXT NOT NULL REFERENCES travel_classes(class_code),
            total_capacity INTEGER NOT NULL CHECK (total_capacity > 0),
            base_fare REAL NOT NULL CHECK (base_fare >= 0),
            PRIMARY KEY (run_id, class_code)
        );

        CREATE TABLE bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL REFERENCES users(user_id),
            run_id INTEGER NOT NULL REFERENCES train_runs(run_id),
            from_station_code TEXT NOT NULL REFERENCES stations(station_code),
            to_station_code TEXT NOT NULL REFERENCES stations(station_code),
            class_code TEXT NOT NULL REFERENCES travel_classes(class_code),
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_fare REAL NOT NULL CHECK (total_fare >= 0),
            booking_status TEXT NOT NULL DEFAULT 'CONFIRMED' CHECK (booking_status IN ('CONFIRMED', 'CANCELLED'))
        );

        CREATE TABLE booking_passengers (
            booking_id INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
            passenger_seq INTEGER NOT NULL CHECK (passenger_seq BETWEEN 1 AND 6),
            passenger_name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK (age BETWEEN 1 AND 120),
            gender TEXT NOT NULL CHECK (gender IN ('MALE', 'FEMALE', 'OTHER')),
            PRIMARY KEY (booking_id, passenger_seq)
        );

        CREATE TABLE booking_cancellation_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            pnr TEXT NOT NULL,
            cancelled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cancellation_reason TEXT DEFAULT 'User requested online cancellation'
        );

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
            COALESCE(COUNT(bp.passenger_seq), 0) AS booked_seats,
            (tc.total_capacity - COALESCE(COUNT(bp.passenger_seq), 0)) AS available_seats
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

        CREATE TRIGGER trg_booking_cancellation
        AFTER UPDATE OF booking_status ON bookings
        FOR EACH ROW
        WHEN OLD.booking_status = 'CONFIRMED' AND NEW.booking_status = 'CANCELLED'
        BEGIN
            INSERT INTO booking_cancellation_logs (booking_id, pnr, cancelled_at, cancellation_reason)
            VALUES (NEW.booking_id, NEW.pnr, datetime('now'), 'Status updated to CANCELLED');
        END;
        """)

        # Execute base seed data from seed.sql
        if seed:
            with open(seed_path, "r", encoding="utf-8") as f:
                seed_sql = f.read()
            # Adapt PostgreSQL TRUNCATE and setval for SQLite
            clean_sql = re.sub(r"TRUNCATE\s+TABLE\s+(\w+)(?:\s+CASCADE)?;", r"DELETE FROM \1;", seed_sql, flags=re.IGNORECASE)
            clean_sql = re.sub(r"SELECT\s+setval\([^;]+;", "", clean_sql, flags=re.IGNORECASE)
            cur.executescript(clean_sql)

            _seed_calendar_and_demo_data(cur, is_postgres=False)

        conn.commit()
        conn.close()

def _seed_calendar_and_demo_data(cur, is_postgres=False):
    """
    Populates 90 days of scheduled train runs and class capacities for all 16 trains,
    plus initial demonstration bookings for viva inspection.
    """
    ph = "%s" if is_postgres else "?"
    print("[DB INIT] Generating scheduled runs for all 16 trains across the next 90 days...")
    trains_list = [
        '12302', '12301', '12394', '12393',
        '12952', '12951', '12004', '12003',
        '12626', '12625', '12296', '12295',
        '12650', '12649', '12834', '12833'
    ]

    run_insert_data = []
    cap_insert_data = []
    run_counter = 1
    start_date = date.today()

    for day_offset in range(90):
        current_day = (start_date + timedelta(days=day_offset)).isoformat()
        for train_num in trains_list:
            run_insert_data.append((run_counter, train_num, current_day, 'SCHEDULED'))

            # Configure realistic class fares based on train type
            if train_num in ('12302', '12301', '12952', '12951'):  # Rajdhani Express
                cap_insert_data.append((run_counter, '3AC', 40, 1850.00))
                cap_insert_data.append((run_counter, '2AC', 20, 2650.00))
                cap_insert_data.append((run_counter, '1AC', 10, 4450.00))
            elif train_num in ('12004', '12003'):  # Shatabdi Express
                cap_insert_data.append((run_counter, '2AC', 45, 1150.00))
                cap_insert_data.append((run_counter, '1AC', 15, 1950.00))
            elif train_num in ('12296', '12295'):  # Sanghamitra Express (MAS <-> PNBE <-> SBC)
                cap_insert_data.append((run_counter, 'SL',  72, 850.00))
                cap_insert_data.append((run_counter, '3AC', 48, 1950.00))
                cap_insert_data.append((run_counter, '2AC', 24, 2850.00))
            else:  # Sampark Kranti / Superfast / Express
                cap_insert_data.append((run_counter, 'SL',  72, 650.00))
                cap_insert_data.append((run_counter, '3AC', 48, 1650.00))
                cap_insert_data.append((run_counter, '2AC', 24, 2400.00))

            run_counter += 1

    cur.executemany(f"INSERT INTO train_runs (run_id, train_number, journey_date, status) VALUES ({ph}, {ph}, {ph}, {ph})", run_insert_data)
    cur.executemany(f"INSERT INTO train_class_capacity (run_id, class_code, total_capacity, base_fare) VALUES ({ph}, {ph}, {ph}, {ph})", cap_insert_data)

    # Sample Initial Bookings for Demonstration
    # Booking 1: Confirmed Suresh Kumar on Run 1
    cur.execute("""
    INSERT INTO bookings (booking_id, pnr, user_id, run_id, from_station_code, to_station_code, class_code, total_fare, booking_status)
    VALUES (1, 'PNR8291047', 2, 1, 'NDLS', 'HWH', '3AC', 3700.00, 'CONFIRMED')
    """)
    cur.executemany(f"INSERT INTO booking_passengers (booking_id, passenger_seq, passenger_name, age, gender) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})", [
        (1, 1, 'Suresh Kumar', 42, 'MALE'),
        (1, 2, 'Sunita Kumar', 39, 'FEMALE')
    ])

    # Booking 2: Confirmed Rahul Sharma on Run 5
    cur.execute("""
    INSERT INTO bookings (booking_id, pnr, user_id, run_id, from_station_code, to_station_code, class_code, total_fare, booking_status)
    VALUES (2, 'PNR1029384', 3, 5, 'NDLS', 'BCT', '2AC', 2550.00, 'CONFIRMED')
    """)
    cur.executemany(f"INSERT INTO booking_passengers (booking_id, passenger_seq, passenger_name, age, gender) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})", [
        (2, 1, 'Rahul Sharma', 26, 'MALE')
    ])

    # Booking 3: Cancelled Priya Singh on Run 1
    cur.execute("""
    INSERT INTO bookings (booking_id, pnr, user_id, run_id, from_station_code, to_station_code, class_code, total_fare, booking_status)
    VALUES (3, 'PNR4829102', 4, 1, 'NDLS', 'CNB', '3AC', 1850.00, 'CANCELLED')
    """)
    cur.executemany(f"INSERT INTO booking_passengers (booking_id, passenger_seq, passenger_name, age, gender) VALUES ({ph}, {ph}, {ph}, {ph}, {ph})", [
        (3, 1, 'Priya Singh', 24, 'FEMALE')
    ])
    cur.execute("""
    INSERT INTO booking_cancellation_logs (booking_id, pnr, cancellation_reason)
    VALUES (3, 'PNR4829102', 'User requested online cancellation')
    """)

    if is_postgres:
        cur.execute("SELECT setval('train_runs_run_id_seq', (SELECT COALESCE(MAX(run_id), 1) FROM train_runs));")
        cur.execute("SELECT setval('bookings_booking_id_seq', (SELECT COALESCE(MAX(booking_id), 1) FROM bookings));")
        cur.execute("SELECT setval('booking_cancellation_logs_log_id_seq', (SELECT COALESCE(MAX(log_id), 1) FROM booking_cancellation_logs));")

    print(f"[DB INIT] Database initialization complete! Seeded {len(run_insert_data)} train runs and {len(cap_insert_data)} class capacity records.")

if __name__ == "__main__":
    target = sys.argv[2] if len(sys.argv) > 2 else None
    init_database(seed=True, engine=target)
