"""
Railway Reservation System - Flask Web Application
Course: Second-Year B.Tech DBMS Project
Database: PostgreSQL via psycopg direct parameterized SQL (NO ORM)
Frontend: HTML, Tailwind CSS, vanilla JavaScript, Jinja2 templates
"""

import os
import random
import string
from datetime import date, datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from db import get_connection

# Load environment configuration
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-railway-secret-key-123456789")

# -----------------------------------------------------------------------------
# Authentication & Authorization Decorators
# -----------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in to access this page.", "info")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please sign in with administrator credentials.", "info")
            return redirect(url_for("login", next=request.url))
        if session.get("role") != "ADMIN":
            flash("Access denied: Administrator privileges required.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function

# -----------------------------------------------------------------------------
# Helper: Generate Unique 10-Character PNR
# -----------------------------------------------------------------------------
def generate_unique_pnr(conn):
    """
    Generates a unique 10-character PNR string (e.g. PNR + 7 random digits)
    and verifies it does not already exist in the database.
    """
    with conn.cursor() as cur:
        while True:
            digits = "".join(random.choices(string.digits, k=7))
            candidate_pnr = f"PNR{digits}"
            cur.execute("SELECT 1 FROM bookings WHERE pnr = %s", (candidate_pnr,))
            if not cur.fetchone():
                return candidate_pnr

# -----------------------------------------------------------------------------
# Route 1: Home Page & Search Interface
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    today_str = date.today().isoformat()
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT station_code, station_name, city FROM stations ORDER BY station_name ASC")
                stations = cur.fetchall()
    except Exception as exc:
        stations = []
        flash(f"Database connection error: {exc}. Please verify PostgreSQL is running and configured.", "error")

    return render_template("index.html", stations=stations, today_str=today_str)

# -----------------------------------------------------------------------------
# Route 2: Train Search Results (Directional Route Order Validation)
# -----------------------------------------------------------------------------
@app.route("/search")
def search_trains():
    from_stn = request.args.get("from_station", "").strip().upper()
    to_stn = request.args.get("to_station", "").strip().upper()
    journey_date_str = request.args.get("journey_date", "").strip()

    if not from_stn or not to_stn or not journey_date_str:
        flash("Please provide origin station, destination station, and journey date.", "error")
        return redirect(url_for("index"))

    if from_stn == to_stn:
        flash("Origin and Destination stations cannot be identical.", "error")
        return redirect(url_for("index"))

    try:
        journey_date = datetime.strptime(journey_date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid journey date format. Please use YYYY-MM-DD.", "error")
        return redirect(url_for("index"))

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Retrieve station metadata
                cur.execute("SELECT station_code, station_name, city FROM stations WHERE station_code = %s", (from_stn,))
                from_station = cur.fetchone()
                cur.execute("SELECT station_code, station_name, city FROM stations WHERE station_code = %s", (to_stn,))
                to_station = cur.fetchone()

                if not from_station or not to_station:
                    flash("One or both selected stations could not be found.", "error")
                    return redirect(url_for("index"))

                # Strict directional route search: destination stop must appear AFTER origin stop
                search_query = """
                SELECT 
                    tr.run_id,
                    tr.train_number,
                    t.train_name,
                    tr.journey_date,
                    ts_from.departure_time,
                    ts_to.arrival_time,
                    (ts_to.distance_km - ts_from.distance_km) AS distance_km,
                    (ts_to.stop_sequence - ts_from.stop_sequence - 1) AS stops_between,
                    (SELECT COUNT(*) FROM train_stops WHERE train_number = t.train_number) AS total_intermediate_stops,
                    s_origin.station_name AS train_source,
                    s_dest.station_name AS train_destination
                FROM train_runs tr
                JOIN trains t ON tr.train_number = t.train_number
                JOIN train_stops ts_from ON t.train_number = ts_from.train_number AND ts_from.station_code = %s
                JOIN train_stops ts_to ON t.train_number = ts_to.train_number AND ts_to.station_code = %s
                JOIN stations s_origin ON t.source_station_code = s_origin.station_code
                JOIN stations s_dest ON t.destination_station_code = s_dest.station_code
                WHERE tr.journey_date = %s
                  AND tr.status = 'SCHEDULED'
                  AND ts_from.stop_sequence < ts_to.stop_sequence
                ORDER BY ts_from.departure_time ASC;
                """
                cur.execute(search_query, (from_stn, to_stn, journey_date))
                raw_trains = cur.fetchall()

                # For each matching train, fetch class-wise availability & fare
                trains = []
                for tr in raw_trains:
                    class_query = """
                    SELECT 
                        tc.class_code,
                        cl.class_name,
                        tc.total_capacity,
                        tc.base_fare,
                        (tc.total_capacity - COALESCE(
                            (SELECT COUNT(bp.passenger_seq)
                             FROM bookings b
                             JOIN booking_passengers bp ON b.booking_id = bp.booking_id
                             WHERE b.run_id = tc.run_id
                               AND b.class_code = tc.class_code
                               AND b.booking_status = 'CONFIRMED'), 0))::INT AS available_seats
                    FROM train_class_capacity tc
                    JOIN travel_classes cl ON tc.class_code = cl.class_code
                    WHERE tc.run_id = %s
                    ORDER BY tc.base_fare ASC;
                    """
                    cur.execute(class_query, (tr["run_id"],))
                    classes = cur.fetchall()

                    train_item = dict(tr)
                    train_item["classes"] = classes
                    trains.append(train_item)

    except Exception as exc:
        flash(f"Error querying trains: {exc}", "error")
        return redirect(url_for("index"))

    return render_template(
        "search_results.html",
        from_station=from_station,
        to_station=to_station,
        journey_date=journey_date_str,
        trains=trains
    )

# -----------------------------------------------------------------------------
# Route 3: Train Timetable & Route Schedule
# -----------------------------------------------------------------------------
@app.route("/train/<train_number>")
def train_schedule(train_number):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Train info
                cur.execute("""
                SELECT t.train_number, t.train_name, t.source_station_code, t.destination_station_code,
                       s1.station_name AS source_name, s2.station_name AS dest_name
                FROM trains t
                JOIN stations s1 ON t.source_station_code = s1.station_code
                JOIN stations s2 ON t.destination_station_code = s2.station_code
                WHERE t.train_number = %s;
                """, (train_number,))
                train = cur.fetchone()

                if not train:
                    flash(f"Train {train_number} not found.", "error")
                    return redirect(url_for("index"))

                # Ordered stops from weak entity train_stops
                cur.execute("""
                SELECT 
                    ts.stop_sequence,
                    ts.station_code,
                    s.station_name,
                    s.city,
                    s.state,
                    ts.arrival_time,
                    ts.departure_time,
                    ts.halt_minutes,
                    ts.distance_km
                FROM train_stops ts
                JOIN stations s ON ts.station_code = s.station_code
                WHERE ts.train_number = %s
                ORDER BY ts.stop_sequence ASC;
                """, (train_number,))
                stops = cur.fetchall()

    except Exception as exc:
        flash(f"Error loading train schedule: {exc}", "error")
        return redirect(url_for("index"))

    return render_template("train_schedule.html", train=train, stops=stops)

# -----------------------------------------------------------------------------
# Route 4: Passenger Booking (Atomic PostgreSQL Transaction & Concurrency Control)
# -----------------------------------------------------------------------------
@app.route("/book", methods=["GET", "POST"])
@login_required
def book_ticket():
    if request.method == "GET":
        run_id = request.args.get("run_id")
        class_code = request.args.get("class_code")
        from_stn = request.args.get("from_station")
        to_stn = request.args.get("to_station")

        if not all([run_id, class_code, from_stn, to_stn]):
            flash("Missing booking parameter details.", "error")
            return redirect(url_for("index"))

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    # Validate run and train
                    cur.execute("""
                    SELECT tr.run_id, tr.train_number, tr.journey_date, t.train_name
                    FROM train_runs tr
                    JOIN trains t ON tr.train_number = t.train_number
                    WHERE tr.run_id = %s AND tr.status = 'SCHEDULED';
                    """, (run_id,))
                    train_run = cur.fetchone()

                    # Validate stations
                    cur.execute("SELECT station_code, station_name FROM stations WHERE station_code = %s", (from_stn,))
                    from_station = cur.fetchone()
                    cur.execute("SELECT station_code, station_name FROM stations WHERE station_code = %s", (to_stn,))
                    to_station = cur.fetchone()

                    # Validate class & capacity
                    cur.execute("SELECT class_code, class_name FROM travel_classes WHERE class_code = %s", (class_code,))
                    travel_class = cur.fetchone()

                    cur.execute("""
                    SELECT total_capacity, base_fare
                    FROM train_class_capacity
                    WHERE run_id = %s AND class_code = %s;
                    """, (run_id, class_code))
                    class_capacity = cur.fetchone()

                    if not all([train_run, from_station, to_station, travel_class, class_capacity]):
                        flash("Invalid booking selection details.", "error")
                        return redirect(url_for("index"))

                    # Compute live available seats
                    cur.execute("""
                    SELECT COUNT(bp.passenger_seq) AS booked_count
                    FROM bookings b
                    JOIN booking_passengers bp ON b.booking_id = bp.booking_id
                    WHERE b.run_id = %s AND b.class_code = %s AND b.booking_status = 'CONFIRMED';
                    """, (run_id, class_code))
                    booked_count = cur.fetchone()["booked_count"]
                    available_seats = class_capacity["total_capacity"] - booked_count

                    if available_seats <= 0:
                        flash(f"Sorry, no seats are currently available in class {class_code}.", "error")
                        return redirect(url_for("search_trains", from_station=from_stn, to_station=to_stn, journey_date=train_run["journey_date"]))

        except Exception as exc:
            flash(f"Error preparing booking: {exc}", "error")
            return redirect(url_for("index"))

        return render_template(
            "book.html",
            train_run=train_run,
            train=train_run,
            from_station=from_station,
            to_station=to_station,
            travel_class=travel_class,
            class_capacity=class_capacity,
            available_seats=available_seats
        )

    # POST: Process Booking Submission atomically
    run_id = request.form.get("run_id")
    class_code = request.form.get("class_code")
    from_stn = request.form.get("from_station")
    to_stn = request.form.get("to_station")

    passenger_names = request.form.getlist("passenger_name[]")
    passenger_ages = request.form.getlist("passenger_age[]")
    passenger_genders = request.form.getlist("passenger_gender[]")

    num_passengers = len(passenger_names)
    if num_passengers < 1 or num_passengers > 6:
        flash("You must specify between 1 and 6 passengers per ticket reservation.", "error")
        return redirect(request.url)

    # Server-side validation of passenger data
    validated_passengers = []
    for i in range(num_passengers):
        name = passenger_names[i].strip()
        age_str = passenger_ages[i].strip()
        gender = passenger_genders[i].strip().upper()

        if not name:
            flash("All passenger names must be non-empty.", "error")
            return redirect(request.url)

        try:
            age = int(age_str)
            if age < 1 or age > 120:
                raise ValueError()
        except ValueError:
            flash(f"Invalid age for passenger '{name}'. Age must be between 1 and 120.", "error")
            return redirect(request.url)

        if gender not in ("MALE", "FEMALE", "OTHER"):
            gender = "OTHER"

        validated_passengers.append((i + 1, name, age, gender))

    user_id = session["user_id"]

    # ATOMIC TRANSACTION WITH ROW LOCKING
    try:
        with get_connection(autocommit=False) as conn:
            with conn.cursor() as cur:
                # 1. Lock the capacity row using SELECT ... FOR UPDATE to prevent concurrency race conditions
                cur.execute("""
                SELECT total_capacity, base_fare
                FROM train_class_capacity
                WHERE run_id = %s AND class_code = %s
                FOR UPDATE;
                """, (run_id, class_code))
                capacity_row = cur.fetchone()

                if not capacity_row:
                    conn.rollback()
                    flash("Capacity configuration not found for selected run and class.", "error")
                    return redirect(url_for("index"))

                total_capacity = capacity_row["total_capacity"]
                base_fare = capacity_row["base_fare"]

                # 2. Re-verify currently confirmed booked seats under lock
                cur.execute("""
                SELECT COUNT(bp.passenger_seq) AS booked_count
                FROM bookings b
                JOIN booking_passengers bp ON b.booking_id = bp.booking_id
                WHERE b.run_id = %s AND b.class_code = %s AND b.booking_status = 'CONFIRMED';
                """, (run_id, class_code))
                current_booked = cur.fetchone()["booked_count"]

                available = total_capacity - current_booked
                if available < num_passengers:
                    conn.rollback()
                    flash(f"Insufficient capacity! Only {available} seat(s) remain, but {num_passengers} requested. Transaction aborted.", "error")
                    return redirect(url_for("index"))

                # 3. Calculate actual total fare on the backend (do not trust client)
                total_fare = float(base_fare) * num_passengers

                # 4. Generate unique PNR
                pnr = generate_unique_pnr(conn)

                # 5. Insert Booking record
                cur.execute("""
                INSERT INTO bookings (pnr, user_id, run_id, from_station_code, to_station_code, class_code, total_fare, booking_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'CONFIRMED')
                RETURNING booking_id;
                """, (pnr, user_id, run_id, from_stn, to_stn, class_code, total_fare))
                booking_id = cur.fetchone()["booking_id"]

                # 6. Insert Passenger records (Weak entity)
                for seq, name, age, gender in validated_passengers:
                    cur.execute("""
                    INSERT INTO booking_passengers (booking_id, passenger_seq, passenger_name, age, gender)
                    VALUES (%s, %s, %s, %s, %s);
                    """, (booking_id, seq, name, age, gender))

            # Commit the atomic transaction
            conn.commit()

        flash(f"Booking successful! Your PNR is {pnr}.", "success")
        return redirect(url_for("booking_confirmed", pnr=pnr))

    except Exception as exc:
        flash(f"Transaction failed and was rolled back: {exc}", "error")
        return redirect(url_for("index"))

# -----------------------------------------------------------------------------
# Route 5: Booking Confirmation Page
# -----------------------------------------------------------------------------
@app.route("/booking-confirmed/<pnr>")
@login_required
def booking_confirmed(pnr):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT 
                    b.pnr, b.booking_id, b.booking_date, b.total_fare, b.booking_status,
                    b.from_station_code AS from_station, b.to_station_code AS to_station,
                    b.class_code, tr.journey_date, tr.train_number, t.train_name
                FROM bookings b
                JOIN train_runs tr ON b.run_id = tr.run_id
                JOIN trains t ON tr.train_number = t.train_number
                WHERE b.pnr = %s AND b.user_id = %s;
                """, (pnr, session["user_id"]))
                booking = cur.fetchone()

                if not booking:
                    flash("Booking confirmation record not found.", "error")
                    return redirect(url_for("my_bookings"))

                cur.execute("SELECT COUNT(*) AS count FROM booking_passengers WHERE booking_id = %s", (booking["booking_id"],))
                passenger_count = cur.fetchone()["count"]

    except Exception as exc:
        flash(f"Error loading confirmation: {exc}", "error")
        return redirect(url_for("my_bookings"))

    return render_template("booking_confirmed.html", booking=booking, passenger_count=passenger_count)

# -----------------------------------------------------------------------------
# Route 6: PNR Status Enquiry (Public Non-Sensitive Lookup)
# -----------------------------------------------------------------------------
@app.route("/pnr")
def pnr_status():
    pnr_query = request.args.get("pnr", "").strip().upper()
    booking = None

    if pnr_query:
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT 
                        b.pnr, b.booking_status, tr.journey_date, b.class_code, b.user_id,
                        b.from_station_code AS from_station, b.to_station_code AS to_station,
                        t.train_number, t.train_name,
                        COUNT(bp.passenger_seq) AS passenger_count
                    FROM bookings b
                    JOIN train_runs tr ON b.run_id = tr.run_id
                    JOIN trains t ON tr.train_number = t.train_number
                    LEFT JOIN booking_passengers bp ON b.booking_id = bp.booking_id
                    WHERE b.pnr = %s
                    GROUP BY b.pnr, b.booking_status, tr.journey_date, b.class_code, b.user_id,
                             b.from_station_code, b.to_station_code, t.train_number, t.train_name;
                    """, (pnr_query,))
                    booking = cur.fetchone()
        except Exception as exc:
            flash(f"Error querying PNR: {exc}", "error")

    return render_template("pnr_status.html", pnr_query=pnr_query, booking=booking)

# -----------------------------------------------------------------------------
# Route 7: User's Booking History
# -----------------------------------------------------------------------------
@app.route("/my-bookings")
@login_required
def my_bookings():
    user_id = session["user_id"]
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                SELECT 
                    b.pnr, b.booking_id, b.booking_date, b.total_fare, b.booking_status,
                    b.from_station_code, b.to_station_code, b.class_code,
                    tr.journey_date, t.train_number, t.train_name,
                    COUNT(bp.passenger_seq) AS passenger_count
                FROM bookings b
                JOIN train_runs tr ON b.run_id = tr.run_id
                JOIN trains t ON tr.train_number = t.train_number
                LEFT JOIN booking_passengers bp ON b.booking_id = bp.booking_id
                WHERE b.user_id = %s
                GROUP BY b.pnr, b.booking_id, b.booking_date, b.total_fare, b.booking_status,
                         b.from_station_code, b.to_station_code, b.class_code,
                         tr.journey_date, t.train_number, t.train_name
                ORDER BY b.booking_date DESC;
                """, (user_id,))
                bookings = cur.fetchall()
    except Exception as exc:
        flash(f"Error loading booking history: {exc}", "error")
        bookings = []

    return render_template("history.html", bookings=bookings)

# -----------------------------------------------------------------------------
# Route 8: View E-Ticket & Printable Reservation Slip
# -----------------------------------------------------------------------------
@app.route("/ticket/<pnr>")
@login_required
def view_ticket(pnr):
    user_id = session["user_id"]
    is_admin = session.get("role") == "ADMIN"

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Retrieve booking with route and user information
                cur.execute("""
                SELECT 
                    b.booking_id, b.pnr, b.booking_date, b.total_fare, b.booking_status,
                    b.user_id, b.from_station_code, b.to_station_code, b.class_code,
                    s_from.station_name AS from_station_name,
                    s_to.station_name AS to_station_name,
                    ts_from.departure_time,
                    ts_to.arrival_time,
                    tr.journey_date,
                    t.train_number, t.train_name,
                    cl.class_name,
                    u.full_name AS booked_by_name,
                    u.email AS booked_by_email
                FROM bookings b
                JOIN users u ON b.user_id = u.user_id
                JOIN train_runs tr ON b.run_id = tr.run_id
                JOIN trains t ON tr.train_number = t.train_number
                JOIN travel_classes cl ON b.class_code = cl.class_code
                JOIN stations s_from ON b.from_station_code = s_from.station_code
                JOIN stations s_to ON b.to_station_code = s_to.station_code
                LEFT JOIN train_stops ts_from ON t.train_number = ts_from.train_number AND b.from_station_code = ts_from.station_code
                LEFT JOIN train_stops ts_to ON t.train_number = ts_to.train_number AND b.to_station_code = ts_to.station_code
                WHERE b.pnr = %s;
                """, (pnr,))
                booking = cur.fetchone()

                if not booking:
                    flash(f"Ticket for PNR {pnr} not found.", "error")
                    return redirect(url_for("my_bookings"))

                # Authorization check: only booking owner or admin can view ticket
                if booking["user_id"] != user_id and not is_admin:
                    flash("Unauthorized: You do not have permission to view this ticket.", "error")
                    return redirect(url_for("my_bookings"))

                # Retrieve passengers (Weak entity)
                cur.execute("""
                SELECT passenger_seq, passenger_name, age, gender
                FROM booking_passengers
                WHERE booking_id = %s
                ORDER BY passenger_seq ASC;
                """, (booking["booking_id"],))
                passengers = cur.fetchall()

    except Exception as exc:
        flash(f"Error fetching ticket details: {exc}", "error")
        return redirect(url_for("my_bookings"))

    return render_template("ticket.html", booking=booking, passengers=passengers)

# -----------------------------------------------------------------------------
# Route 9: Cancel Booking (Status Update + Restores Capacity + Trigger Audit)
# -----------------------------------------------------------------------------
@app.route("/cancel/<pnr>", methods=["POST"])
@login_required
def cancel_ticket(pnr):
    user_id = session["user_id"]
    is_admin = session.get("role") == "ADMIN"

    try:
        with get_connection(autocommit=False) as conn:
            with conn.cursor() as cur:
                # Verify booking ownership and current status
                cur.execute("SELECT booking_id, user_id, booking_status FROM bookings WHERE pnr = %s", (pnr,))
                booking = cur.fetchone()

                if not booking:
                    conn.rollback()
                    flash(f"Booking with PNR {pnr} does not exist.", "error")
                    return redirect(url_for("my_bookings"))

                if booking["user_id"] != user_id and not is_admin:
                    conn.rollback()
                    flash("Unauthorized cancellation request.", "error")
                    return redirect(url_for("my_bookings"))

                if booking["booking_status"] == "CANCELLED":
                    conn.rollback()
                    flash("This booking has already been cancelled.", "info")
                    return redirect(url_for("view_ticket", pnr=pnr))

                # Update status to CANCELLED (does NOT delete booking, preserves history & activates trigger)
                cur.execute("""
                UPDATE bookings
                SET booking_status = 'CANCELLED'
                WHERE pnr = %s AND booking_status = 'CONFIRMED';
                """, (pnr,))

            conn.commit()

        flash(f"Booking {pnr} was successfully cancelled. Reserved capacity has been restored.", "success")
    except Exception as exc:
        flash(f"Error cancelling booking: {exc}", "error")

    return redirect(url_for("view_ticket", pnr=pnr))

# -----------------------------------------------------------------------------
# Route 10: User Authentication (Login, Register, Logout)
# -----------------------------------------------------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT user_id, email, password_hash, full_name, role
                    FROM users
                    WHERE email = %s;
                    """, (email,))
                    user = cur.fetchone()

                    if user and check_password_hash(user["password_hash"], password):
                        session.clear()
                        session["user_id"] = user["user_id"]
                        session["user_email"] = user["email"]
                        session["user_name"] = user["full_name"]
                        session["role"] = user["role"]

                        flash(f"Welcome back, {user['full_name']}!", "success")
                        next_url = request.args.get("next")
                        return redirect(next_url or url_for("index"))
                    else:
                        flash("Invalid email or password. Please try again.", "error")

        except Exception as exc:
            flash(f"Login database error: {exc}", "error")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not all([full_name, email, phone, password]):
            flash("All registration fields are required.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "error")
            return redirect(url_for("register"))

        pw_hash = generate_password_hash(password)

        try:
            with get_connection(autocommit=True) as conn:
                with conn.cursor() as cur:
                    # Check unique email
                    cur.execute("SELECT 1 FROM users WHERE email = %s", (email,))
                    if cur.fetchone():
                        flash("An account with this email address already exists.", "error")
                        return redirect(url_for("register"))

                    cur.execute("""
                    INSERT INTO users (email, password_hash, full_name, phone, role)
                    VALUES (%s, %s, %s, %s, 'PASSENGER')
                    RETURNING user_id;
                    """, (email, pw_hash, full_name, phone))
                    new_user = cur.fetchone()

            flash("Registration successful! You may now sign in.", "success")
            return redirect(url_for("login"))

        except Exception as exc:
            flash(f"Registration error: {exc}", "error")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("index"))

# -----------------------------------------------------------------------------
# Route 11: Administrator Dashboard (Queries Mandatory SQL VIEW & Metrics)
# -----------------------------------------------------------------------------
@app.route("/admin")
@admin_required
def admin_dashboard():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                # System metrics
                cur.execute("""
                SELECT 
                    COUNT(*) AS total_bookings,
                    COUNT(*) FILTER (WHERE booking_status = 'CONFIRMED') AS confirmed_bookings,
                    COUNT(*) FILTER (WHERE booking_status = 'CANCELLED') AS cancelled_bookings,
                    COALESCE(SUM(total_fare) FILTER (WHERE booking_status = 'CONFIRMED'), 0.00) AS total_revenue
                FROM bookings;
                """)
                metrics_res = cur.fetchone()

                cur.execute("""
                SELECT COUNT(bp.passenger_seq) AS total_passengers
                FROM bookings b
                JOIN booking_passengers bp ON b.booking_id = bp.booking_id
                WHERE b.booking_status = 'CONFIRMED';
                """)
                passenger_res = cur.fetchone()

                metrics = {
                    "total_bookings": metrics_res["total_bookings"] or 0,
                    "confirmed_bookings": metrics_res["confirmed_bookings"] or 0,
                    "cancelled_bookings": metrics_res["cancelled_bookings"] or 0,
                    "total_revenue": float(metrics_res["total_revenue"] or 0.0),
                    "total_passengers": passenger_res["total_passengers"] or 0
                }

                # QUERY THE MANDATORY SQL VIEW
                cur.execute("""
                SELECT 
                    run_id, train_number, train_name, journey_date, run_status,
                    class_code, class_name, total_capacity, base_fare, booked_seats, available_seats
                FROM v_train_occupancy_summary
                ORDER BY journey_date DESC, train_number ASC, class_code ASC;
                """)
                occupancy = cur.fetchall()

                # QUERY CANCELLATION AUDIT LOGS (Populated by trigger)
                cur.execute("""
                SELECT log_id, booking_id, pnr, cancelled_at, cancellation_reason
                FROM booking_cancellation_logs
                ORDER BY cancelled_at DESC
                LIMIT 50;
                """)
                logs = cur.fetchall()

    except Exception as exc:
        flash(f"Error loading admin dashboard: {exc}", "error")
        metrics = {"total_bookings": 0, "confirmed_bookings": 0, "cancelled_bookings": 0, "total_revenue": 0.0, "total_passengers": 0}
        occupancy = []
        logs = []

    return render_template("admin.html", metrics=metrics, occupancy=occupancy, logs=logs)

# -----------------------------------------------------------------------------
# Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

    # Pre-verify database connection so there is zero initial delay on first request
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS total_stations FROM stations")
                cnt = cur.fetchone()["total_stations"]
                print(f"[DATABASE READY] Verified {cnt} stations in database.")
    except Exception as exc:
        print(f"[DATABASE WARNING] Initial check note: {exc}")

    print(f"\n========================================================")
    print(f"Railway Reservation System running on http://127.0.0.1:{port}")
    print(f"Open http://127.0.0.1:{port} in your web browser.")
    print(f"========================================================\n")

    app.run(host="127.0.0.1", port=port, debug=debug_mode)
