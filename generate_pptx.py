"""
Generates the comprehensive, professional PowerPoint presentation:
Railway_Reservation_System_Presentation.pptx
Adhering to all mandatory presentation sections.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    # Theme colors
    PRIMARY = RGBColor(15, 30, 54)      # Deep Navy
    ACCENT = RGBColor(2, 132, 199)      # Sky Blue
    ACCENT_LIGHT = RGBColor(224, 242, 254)
    TEXT_DARK = RGBColor(30, 41, 59)    # Slate 800
    TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
    WHITE = RGBColor(255, 255, 255)
    CARD_BG = RGBColor(248, 250, 252)   # Slate 50
    CARD_BORDER = RGBColor(203, 213, 225) # Slate 300
    GREEN = RGBColor(22, 101, 52)
    GREEN_BG = RGBColor(220, 252, 231)

    def add_header(slide, title_text, category_text="DBMS COURSE PROJECT"):
        # Header ribbon
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = PRIMARY
        header_shape.line.fill.background()

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.3))
        cat_tf = cat_box.text_frame
        cat_tf.word_wrap = True
        p_cat = cat_tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT

        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.5), Inches(0.65))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = WHITE

    def add_card(slide, left, top, width, height, title, items, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(Inches(left + 0.2), Inches(top + 0.15), Inches(width - 0.4), Inches(height - 0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        if title:
            p_title = tf.paragraphs[0]
            p_title.text = title
            p_title.font.size = Pt(15)
            p_title.font.bold = True
            p_title.font.color.rgb = PRIMARY
            p_title.space_after = Pt(8)

        for idx, item in enumerate(items):
            p = tf.add_paragraph() if (title or idx > 0) else tf.paragraphs[0]
            p.text = "• " + item if not item.startswith("  ") else "    - " + item.strip()
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT_DARK
            p.space_after = Pt(5)

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = PRIMARY
    bg1.line.fill.background()

    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "RAILWAY RESERVATION SYSTEM (IRCTC MINI)"
    p0.font.size = Pt(34)
    p0.font.bold = True
    p0.font.color.rgb = WHITE
    p0.space_after = Pt(12)

    p1 = tf1.add_paragraph()
    p1.text = "Design, Normalization, SQL Implementation & Concurrency-Safe Architecture"
    p1.font.size = Pt(18)
    p1.font.color.rgb = ACCENT
    p1.space_after = Pt(28)

    p2 = tf1.add_paragraph()
    p2.text = "A Second-Year B.Tech Database Management Systems (DBMS) Course Project"
    p2.font.size = Pt(14)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_after = Pt(6)

    p3 = tf1.add_paragraph()
    p3.text = "Technology Stack: PostgreSQL | psycopg (Raw Parameterized SQL) | Python Flask | Tailwind CSS"
    p3.font.size = Pt(12)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # =========================================================================
    # SLIDE 2: 1. ABSTRACT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "1. Executive Abstract")
    add_card(s2, 0.8, 1.4, 5.6, 5.6, "Project Scope & Focus", [
        "Modern railway booking requires dependable transactional consistency, route validation, and accurate seat accounting.",
        "This project implements a simplified but complete IRCTC-style Railway Reservation Web Application adhering strictly to second-year B.Tech DBMS academic rigour.",
        "Emphasizes solid relational database foundations rather than complex commercial microservices or ORM abstractions.",
        "Follows professor-specified reference conventions for Chen ER conceptual modeling, 7-step relational conversion, and BCNF/3NF normalization."
    ])
    add_card(s2, 6.8, 1.4, 5.7, 5.6, "Key Architectural Highlights", [
        "Direct Parameterized SQL: All database interactions execute via psycopg with zero ORM overhead to demonstrate pure SQL mastery.",
        "ACID Concurrency Control: Solves the classic ticket overbooking race condition using explicit row-level locking (SELECT ... FOR UPDATE).",
        "Mandatory SQL View: Employs v_train_occupancy_summary for real-time seat availability calculation and administrative reporting.",
        "Directional Route Ordering: Enforces sequence constraints on train stops to validate legitimate forward-direction journeys.",
        "Responsive Vanilla UI: Modern HTML5, Tailwind CSS, and vanilla JavaScript for dynamic passenger reservations without external JS frameworks."
    ])

    # =========================================================================
    # SLIDE 3: 2. MOTIVATION
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "2. Motivation & Problem Statement")
    add_card(s3, 0.8, 1.4, 5.6, 5.6, "Academic & Practical Motivation", [
        "Bridging Theory and Practice: Textbooks frequently demonstrate SQL with toy tables, while commercial systems are obscured by layered ORMs.",
        "IRCTC is one of India's most demanding database systems, making a simplified prototype ideal for demonstrating core DBMS topics.",
        "Showcase Critical DBMS Concepts:",
        "  Entity-Relationship semantics (Weak entities, identifying relationships)",
        "  Rigorous normalization to eliminate anomalies while preserving dependencies",
        "  Atomic transaction control under concurrent multi-user booking pressure",
        "  Database-side automation via triggers and encapsulating logic via views"
    ])
    add_card(s3, 6.8, 1.4, 5.7, 5.6, "Challenges & Scope Guardrails", [
        "Addressed Challenges:",
        "  Preventing phantom bookings when the last remaining seat is contested",
        "  Directional station sequence validation (preventing reverse-order bookings)",
        "  Preserving complete financial & audit history during cancellation",
        "Deliberate Scope Simplifications (Per Project Brief):",
        "  Capacity booked per entire run (no complex seat-overlap segment reuse)",
        "  No physical berth allocation, Tatkal, waiting list, or real payment gateways",
        "  Payment-free, deterministic workflow designed for viva evaluation"
    ])

    # =========================================================================
    # SLIDE 4: 3. PROPOSED SYSTEM
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "3. Proposed System Architecture")
    add_card(s4, 0.8, 1.4, 3.7, 5.6, "1. Frontend Layer", [
        "Tailwind CSS via CDN for responsive, maintainable styling.",
        "Server-rendered Jinja2 HTML templates for SEO, speed, and simplicity.",
        "Vanilla JavaScript for dynamic DOM updates:",
        "  Add/remove passengers (1-6 per booking)",
        "  Instant client-side fare preview calculation",
        "Print-specific stylesheet (@media print) for printable e-tickets."
    ])
    add_card(s4, 4.8, 1.4, 3.7, 5.6, "2. Backend Routing Layer", [
        "Python Flask server-rendered application.",
        "Session-based authentication with role-based access control (Passenger vs Admin).",
        "Password security: Scrypt hashing via werkzeug.security.",
        "Strict input re-validation: Every passenger age, gender, and route sequence validated on backend.",
        "No separate REST API required; clean monolithic architecture."
    ])
    add_card(s4, 8.8, 1.4, 3.7, 5.6, "3. PostgreSQL Engine", [
        "Native PostgreSQL connected via psycopg 3 driver.",
        "Zero ORM: All queries use direct parameterized SQL (%s placeholders).",
        "Full ACID transactions with BEGIN, COMMIT, and ROLLBACK.",
        "Relational Schema: 8-10 normalized relations.",
        "Integrity: PK, FK (CASCADE/RESTRICT), CHECK, UNIQUE, NOT NULL constraints."
    ])

    # =========================================================================
    # SLIDE 5: 4. ER DIAGRAM FOR PROPOSED DB SYSTEM
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "4. ER Conceptual Model (Chen Notation)")
    add_card(s5, 0.8, 1.4, 5.6, 5.6, "Entity Sets & Cardinalities", [
        "Regular (Strong) Entities:",
        "  USERS: (<u>user_id</u>, email [UQ], password_hash, full_name, phone, role)",
        "  STATIONS: (<u>station_code</u>, station_name, city, state)",
        "  TRAINS: (<u>train_number</u>, train_name, source_stn, dest_stn)",
        "  TRAIN_RUNS: (<u>run_id</u>, journey_date, status)",
        "  TRAVEL_CLASSES: (<u>class_code</u>, class_name)",
        "  BOOKINGS: (<u>booking_id</u>, pnr [UQ], booking_date, total_fare, status)",
        "Weak Entities (Double Rectangle):",
        "  TRAIN_STOPS: Owned by TRAINS via HAS_STOPS. Partial key: stop_seq.",
        "  BOOKING_PASSENGERS: Owned by BOOKINGS via CONTAINS. Partial key: passenger_seq."
    ])
    add_card(s5, 6.8, 1.4, 5.7, 5.6, "Relationships & Structural Constraints", [
        "BOOKS (1:N): USERS (0,N) to BOOKINGS (1,1) [Total participation].",
        "CONTAINS (1:N): Identifying relationship. BOOKINGS (1,N) to PASSENGERS (1,1).",
        "OPERATES (1:N): TRAINS (0,N) to TRAIN_RUNS (1,1).",
        "HAS_STOPS (1:N): Identifying relationship. TRAINS (1,N) to TRAIN_STOPS (1,1).",
        "OFFERS_CLASS (M:N): TRAIN_RUNS (1,N) to TRAVEL_CLASSES (0,N) with relationship attributes (total_capacity, base_fare).",
        "STARTS_AT / ENDS_AT (1:N): TRAINS to STATIONS.",
        "Diagram Assets Generated:",
        "  docs/Railway_Reservation_ER_Diagram.drawio (Editable)",
        "  docs/ER_Diagram.svg (Vector Image Export)"
    ])

    # =========================================================================
    # SLIDE 6: 5. INCLUDED RDBMS CONCEPTS (PART 1: MAPPING & NORMALIZATION)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "5. RDBMS Concepts: Mapping & Normalization")
    add_card(s6, 0.8, 1.4, 5.6, 5.6, "7-Step ER-to-Relational Conversion", [
        "Step 1 (Regular Entities): Created USERS, STATIONS, TRAINS, TRAVEL_CLASSES, TRAIN_RUNS with chosen PKs.",
        "Step 2 (Weak Entities):",
        "  train_stops: FK train_number + partial key stop_sequence forms composite PK.",
        "  booking_passengers: FK booking_id + partial key passenger_seq forms composite PK.",
        "Step 3 (Binary 1:1): N/A (decomposed into 1:N).",
        "Step 4 (Binary 1:N): Foreign key placed on N-side (e.g. user_id and run_id in bookings).",
        "Step 5 (Binary M:N): train_class_capacity with composite PK (run_id, class_code) + relationship attributes (capacity, fare).",
        "Steps 6 & 7: Handled through atomic 1NF attributes and binary decompositions."
    ])
    add_card(s6, 6.8, 1.4, 5.7, 5.6, "Functional Dependencies & Normal Forms", [
        "1NF Verified: All attribute domains are atomic; composite candidate keys uniquely identify rows.",
        "2NF Verified: No non-prime attribute is partially dependent on any proper subset of a composite candidate key.",
        "3NF Verified: For every FD X -> Y, either X is a superkey or Y is a prime attribute. No transitive dependencies exist.",
        "Boyce-Codd Normal Form (BCNF) Analysis:",
        "  In all core relations (users, stations, trains, train_stops, train_runs, bookings), every determinant X is a candidate key.",
        "  Strict BCNF compliance achieved across the entire schema without losing functional dependencies."
    ])

    # =========================================================================
    # SLIDE 7: 5. INCLUDED RDBMS CONCEPTS (PART 2: SQL, CONSTRAINTS & TRANSACTIONS)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "5. RDBMS Concepts: Constraints, Views & Triggers")
    add_card(s7, 0.8, 1.4, 5.6, 5.6, "Integrity Constraints & Declarative Rules", [
        "PRIMARY KEY & FOREIGN KEY: Referential integrity with CASCADE on weak entity deletions and RESTRICT on users/bookings.",
        "UNIQUE Constraints: Enforced on users.email, bookings.pnr, and (train_number, journey_date).",
        "CHECK Constraints:",
        "  chk_train_endpoints: (source_stn <> dest_stn)",
        "  chk_passengers_age: (age BETWEEN 1 AND 120)",
        "  chk_passengers_gender: (gender IN ('MALE','FEMALE','OTHER'))",
        "  chk_passengers_seq: (passenger_seq BETWEEN 1 AND 6)",
        "  chk_cap_total & base_fare: (capacity > 0 AND base_fare >= 0)"
    ])
    add_card(s7, 6.8, 1.4, 5.7, 5.6, "SQL Views, Triggers & Transactions", [
        "Mandatory SQL VIEW (v_train_occupancy_summary):",
        "  Hides 5-table JOINs and passenger aggregations.",
        "  Exposes real-time booked_seats and available_seats.",
        "Database Trigger (trg_booking_cancellation):",
        "  AFTER UPDATE OF booking_status ON bookings.",
        "  Automatically records cancellation timestamps and reasons into booking_cancellation_logs.",
        "ACID Transactions:",
        "  Atomically reserves seats and passenger rows.",
        "  Cancels tickets while preserving history and restoring seat pool."
    ])

    # =========================================================================
    # SLIDE 8: 6. WORKFLOW
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "6. End-to-End System Workflow")
    add_card(s8, 0.8, 1.4, 2.8, 5.6, "1. Search", [
        "User selects Source, Destination, and Date.",
        "Backend queries stations and train_stops.",
        "Directional Route Filter:",
        "  Matches trains where source_seq < dest_seq.",
        "Calculates distance, halts, and departure/arrival times."
    ])
    add_card(s8, 3.8, 1.4, 2.8, 5.6, "2. Availability", [
        "Fetches class capacities for the run.",
        "Subtracts active confirmed passengers from total capacity.",
        "Displays real-time availability badge (AVL X) and base fare.",
        "Disables booking button if sold out."
    ])
    add_card(s8, 6.8, 1.4, 2.8, 5.6, "3. Reservation", [
        "Authenticated user inputs 1-6 passenger details.",
        "Vanilla JS calculates live fare preview.",
        "PostgreSQL Transaction:",
        "  Acquires row lock on capacity.",
        "  Validates capacity >= passengers.",
        "  Generates unique PNR.",
        "  Inserts booking & passenger rows.",
        "  Commits atomically."
    ])
    add_card(s8, 9.8, 1.4, 2.7, 5.6, "4. Ticket & Cancellation", [
        "Redirects to Booking Confirmation.",
        "Generates printable Electronic Reservation Slip (ERS).",
        "Public PNR enquiry protects passenger personal data.",
        "Cancellation updates status to CANCELLED, restoring capacity and firing audit trigger."
    ])

    # =========================================================================
    # SLIDE 9: 7. IMPLEMENTATION DETAILS (SLIDE 1 OF 4) - RELATIONAL SCHEMA
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "7. Implementation: Relational Schema & DDL", "IMPLEMENTATION (1/4)")
    add_card(s9, 0.8, 1.4, 5.6, 5.6, "Table Architecture Overview", [
        "users: User accounts with scrypt hashed credentials and role ('PASSENGER', 'ADMIN').",
        "stations: Railway station codes (PK: station_code, e.g. NDLS, HWH, BCT).",
        "trains: Master train registry with source/destination foreign keys.",
        "train_stops: Ordered intermediate route stations with stop sequence, halts, and distance.",
        "train_runs: Date-specific scheduled train operations.",
        "travel_classes: Standard Indian railway classes (SL, 3AC, 2AC, 1AC).",
        "train_class_capacity: Run and class-specific capacity and base fare.",
        "bookings & booking_passengers: Header-detail reservation records."
    ])
    add_card(s9, 6.8, 1.4, 5.7, 5.6, "Key DDL Implementation Excerpt", [
        "CREATE TABLE train_stops (",
        "  train_number VARCHAR(10) REFERENCES trains(train_number) ON DELETE CASCADE,",
        "  stop_sequence INT NOT NULL CHECK (stop_sequence > 0),",
        "  station_code VARCHAR(10) REFERENCES stations(station_code),",
        "  arrival_time TIME, departure_time TIME,",
        "  halt_minutes INT DEFAULT 2, distance_km INT DEFAULT 0,",
        "  PRIMARY KEY (train_number, stop_sequence),",
        "  UNIQUE (train_number, station_code)",
        ");",
        "CREATE TABLE booking_passengers (",
        "  booking_id INT REFERENCES bookings(booking_id) ON DELETE CASCADE,",
        "  passenger_seq INT CHECK (passenger_seq BETWEEN 1 AND 6),",
        "  passenger_name VARCHAR(100) NOT NULL, age INT, gender VARCHAR(10),",
        "  PRIMARY KEY (booking_id, passenger_seq)",
        ");"
    ])

    # =========================================================================
    # SLIDE 10: 7. IMPLEMENTATION DETAILS (SLIDE 2 OF 4) - BACKEND & DIRECT SQL
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "7. Implementation: Backend & Parameterized SQL", "IMPLEMENTATION (2/4)")
    add_card(s10, 0.8, 1.4, 5.6, 5.6, "Flask Application Architecture", [
        "Lightweight server-rendered web application in app.py.",
        "Database abstraction in db.py using psycopg 3 connection context managers.",
        "Row Factory: Uses dict_row for clean column-name template bindings.",
        "Zero ORM Dependency: No SQLAlchemy or query builders; guarantees 100% direct SQL transparency for course evaluation.",
        "Security & Authentication:",
        "  werkzeug.security for password hashing and validation.",
        "  Session cookies with @login_required and @admin_required decorators.",
        "  All input passed via %s placeholders to prevent SQL Injection."
    ])
    add_card(s10, 6.8, 1.4, 5.7, 5.6, "Directional Search SQL Query", [
        "SELECT tr.run_id, tr.train_number, t.train_name,",
        "       ts_from.departure_time, ts_to.arrival_time,",
        "       (ts_to.distance_km - ts_from.distance_km) AS distance_km,",
        "       (ts_to.stop_sequence - ts_from.stop_sequence - 1) AS stops_between",
        "FROM train_runs tr",
        "JOIN trains t ON tr.train_number = t.train_number",
        "JOIN train_stops ts_from ON t.train_number = ts_from.train_number",
        "     AND ts_from.station_code = %s",
        "JOIN train_stops ts_to ON t.train_number = ts_to.train_number",
        "     AND ts_to.station_code = %s",
        "WHERE tr.journey_date = %s AND tr.status = 'SCHEDULED'",
        "  AND ts_from.stop_sequence < ts_to.stop_sequence",
        "ORDER BY ts_from.departure_time ASC;"
    ])

    # =========================================================================
    # SLIDE 11: 7. IMPLEMENTATION DETAILS (SLIDE 3 OF 4) - CONCURRENCY CONTROL
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "7. Implementation: Concurrency & Transactions", "IMPLEMENTATION (3/4)")
    add_card(s11, 0.8, 1.4, 5.6, 5.6, "The Overbooking Race Condition", [
        "The Problem:",
        "  Suppose 1 seat remains in class 3AC.",
        "  Two concurrent users (A and B) submit booking requests simultaneously.",
        "  Without locking, both threads read available_seats = 1.",
        "  Both insert booking records, causing 2 tickets issued for 1 seat (overbooking).",
        "The Solution (Pessimistic Row-Level Lock):",
        "  PostgreSQL SELECT ... FOR UPDATE locks the specific (run_id, class_code) capacity row.",
        "  Thread B waits until Thread A commits or rolls back.",
        "  Thread B re-checks remaining seats, observes 0 available, and aborts cleanly."
    ])
    add_card(s11, 6.8, 1.4, 5.7, 5.6, "Atomic Booking Transaction Code Excerpt", [
        "with get_connection(autocommit=False) as conn:",
        "  with conn.cursor() as cur:",
        "    # 1. Lock capacity row exclusively",
        "    cur.execute(\"SELECT total_capacity, base_fare FROM train_class_capacity \"",
        "                \"WHERE run_id = %s AND class_code = %s FOR UPDATE;\", (run_id, cls))",
        "    cap = cur.fetchone()",
        "    # 2. Count active confirmed bookings",
        "    cur.execute(\"SELECT COUNT(bp.passenger_seq) AS booked FROM bookings b \"",
        "                \"JOIN booking_passengers bp ON b.booking_id = bp.booking_id \"",
        "                \"WHERE b.run_id = %s AND b.class_code = %s AND b.booking_status = 'CONFIRMED';\", (run_id, cls))",
        "    if (cap['total_capacity'] - cur.fetchone()['booked']) < num_passengers:",
        "      conn.rollback()",
        "      raise InsufficientSeatsError()",
        "    # 3. Insert booking & passengers, then commit",
        "    cur.execute(\"INSERT INTO bookings ... RETURNING booking_id;\")",
        "    cur.executemany(\"INSERT INTO booking_passengers ...\")",
        "  conn.commit()"
    ])

    # =========================================================================
    # SLIDE 12: 7. IMPLEMENTATION DETAILS (SLIDE 4 OF 4) - FRONTEND & TAILWIND UI
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "7. Implementation: Responsive Frontend UI", "IMPLEMENTATION (4/4)")
    add_card(s12, 0.8, 1.4, 5.6, 5.6, "Tailwind CSS & Vanilla JS Architecture", [
        "Tailwind CSS via CDN:",
        "  Custom railway theme palette (sky-900, sky-600, slate-800, emerald-600).",
        "  Mobile-first responsive grids and card layouts.",
        "  No Node.js or npm build pipeline required; lightweight production footprint.",
        "Dynamic Vanilla JavaScript (static/js/booking.js):",
        "  Allows passengers to dynamically add rows (up to 6 passengers per booking).",
        "  Auto-renumbers passenger labels and manages remove buttons.",
        "  Performs instant client-side total fare calculation based on selected class base fare.",
        "  Client validation prevents invalid inputs before form submission."
    ])
    add_card(s12, 6.8, 1.4, 5.7, 5.6, "Key Interface Pages", [
        "Search & Availability: Dynamic station dropdowns and date selector displaying real-time AVL counts.",
        "Printable E-Ticket: Official Electronic Reservation Slip with QR branding, passenger manifest, and print-friendly CSS (@media print).",
        "Public PNR Status Enquiry: Safe public status lookup concealing personal passenger names and contacts.",
        "My Bookings History: Chronological ticket ledger with instant cancellation action.",
        "Administrator Dashboard:",
        "  Queries mandatory SQL View v_train_occupancy_summary.",
        "  Live display of trigger audit logs from booking_cancellation_logs.",
        "  Summary metric cards for gross revenue, confirmed, and cancelled tickets."
    ])

    # =========================================================================
    # SLIDE 13: 8. CONCLUSION & FUTURE WORK
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    add_header(s13, "8. Conclusion & Future Work")
    add_card(s13, 0.8, 1.4, 5.6, 5.6, "Project Summary & Outcomes", [
        "Successfully Built: A fully functional, responsive, and robust Railway Reservation System tailored for second-year B.Tech DBMS evaluation.",
        "Pedagogical Achievements:",
        "  Verified adherence to Chen ER modeling rules from S_ER Model.pptx.",
        "  Systematic 7-step mapping from Conversion of ERD to Relational Model_1.pptx.",
        "  Rigorous normalization ensuring BCNF/3NF across all relations.",
        "  Executable proof of SQL constraints, views, triggers, and transactions.",
        "Automated Quality Assurance: 12/12 unit and integration tests passing covering booking, concurrency locks, route direction, and cancellations."
    ])
    add_card(s13, 6.8, 1.4, 5.7, 5.6, "Future Enhancements", [
        "Segment-Wise Dynamic Capacity: Support intermediate station capacity re-use (e.g. seat freed after Kanpur re-sold between Prayagraj and Howrah).",
        "Berth & Coach Allocation Engine: Auto-assigning specific coach numbers (B1, B2) and berth types (Lower, Upper, Side Lower).",
        "Waitlist & RAC Queues: Priority queue data structures and automated ticket confirmation cascades upon cancellation.",
        "Tatkal & Dynamic Surge Pricing: Distance-based and demand-based progressive fare structures.",
        "Production Deployment: Seamless containerization or deployment to Render web services with managed Render PostgreSQL instances."
    ])

    # =========================================================================
    # SLIDE 14: 9. REFERENCES
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    add_header(s14, "9. Academic & Technical References")
    add_card(s14, 0.8, 1.4, 11.7, 5.6, "Course References & Recommended Literature", [
        "1. Professor Reference Presentation 1: 'S_ER Model.pptx' — Entity-Relationship modeling, weak entities, attributes, cardinalities, and structural min-max constraints.",
        "2. Professor Reference Presentation 2: 'Conversion of ERD to Relational Model_1.pptx' — The 7-step ER-to-relational mapping algorithm.",
        "3. Professor Reference Presentation 3: 'SQL_Chapter_DB_1.pptx' — SQL DDL, DML, constraints, complex JOINs, GROUP BY / HAVING, subqueries, views, triggers, and transactions.",
        "4. Elmasri, R., & Navathe, S. B. (2015). 'Fundamentals of Database Systems' (7th ed.). Pearson. (Chapters on ER Modeling, Relational Mapping, and Normalization).",
        "5. Silberschatz, A., Korth, H. F., & Sudarshan, S. (2019). 'Database System Concepts' (7th ed.). McGraw-Hill. (Chapters on Transactions, Concurrency Control, and BCNF).",
        "6. PostgreSQL Global Development Group. (2024). 'PostgreSQL 16 Documentation'. Available: https://www.postgresql.org/docs/current/ (Explicit Locking & Views).",
        "7. The Pallets Projects. (2024). 'Flask Documentation (3.0.x)'. Available: https://flask.palletsprojects.com/.",
        "8. Tailwind Labs Inc. (2024). 'Tailwind CSS Documentation'. Available: https://tailwindcss.com/docs."
    ])

    output_path = "D:/dbms_project/Railway_Reservation_System_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_presentation()
