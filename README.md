# Railway Reservation System

A full-stack, concurrency-safe Railway Reservation System designed and implemented for an undergraduate Database Management Systems (DBMS) curriculum. The application demonstrates core relational database principles including Entity-Relationship (ER) modeling, Boyce-Codd Normal Form (BCNF) schema decomposition, ACID transactions with pessimistic row-level locking, automated database triggers, complex SQL views, and direct parameterized query execution without an Object-Relational Mapper (ORM).

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-00c7b7?style=flat-square&logo=render&logoColor=white)](https://mini-irctc.onrender.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2018-336791?style=flat-square&logo=postgresql&logoColor=white)](https://neon.tech/)
[![Python](https://img.shields.io/badge/Backend-Python%203.13%20%2F%20Flask-3776AB?style=flat-square&logo=python&logoColor=white)](https://flask.palletsprojects.com/)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

---

## Live Deployment and Demonstration

* **Production URL:** [https://mini-irctc.onrender.com/](https://mini-irctc.onrender.com/)
* **Database Infrastructure:** Neon Serverless PostgreSQL 18 (AWS `ap-southeast-1`)
* **Web Service:** Render PaaS with Gunicorn WSGI container

### Pre-Configured Demonstration Accounts

| Role | Email | Password | Access and Capabilities |
| :--- | :--- | :--- | :--- |
| **Passenger** | `passenger@railway.com` | `passenger123` | Route search, multi-passenger booking (1–6), printable E-Ticket, ticket cancellation |
| **Administrator** | `admin@railway.com` | `admin123` | Operations dashboard, SQL View monitoring, cancellation audit inspection |

**Sample Demonstration PNR Identifiers:**
* `PNR1029384`: Active confirmed reservation on Train 12952 (Mumbai Rajdhani Express)
* `PNR4829102`: Cancelled reservation (demonstrates status transition and trigger audit logging)

---

## System Capabilities and Database Architecture

* **Directional Route Validation:** Enforces forward-direction station ordering using stop sequence numbers (`stop_sequence(from) < stop_sequence(to)`). Reverse-direction queries are rejected.
* **Concurrency-Safe Atomic Bookings:** Employs pessimistic row-level locking (`SELECT ... FOR UPDATE`) on class capacity records within an explicit transaction to prevent overbooking anomalies under concurrent user traffic.
* **Mandatory SQL View (`v_train_occupancy_summary`):** Encapsulates multi-table joins and real-time seat accounting to provide operational metrics for administrative monitoring.
* **Automated Audit Trigger (`trg_booking_cancellation`):** An event-driven database trigger automatically records an immutable cancellation audit log, restores class seat capacity, and preserves transaction history.
* **Public PNR Enquiry with Privacy Protection:** Conceals passenger names and personal details from public search queries while returning itinerary status and route metadata.
* **Printable Electronic Reservation Slip (ERS):** Clean, print-ready ticket layout generated via `@media print` CSS rules.
* **Normalized Relational Schema (BCNF):** Ten tables derived systematically through the 7-step ER-to-relational mapping algorithm, all verified in Boyce-Codd Normal Form.

---

## Technology Stack

* **Application Tier:** Python 3.13, Flask (server-rendered Jinja2 templates, session management with Scrypt password hashing)
* **Database Driver:** `psycopg 3` executing direct parameterized SQL queries (`%s` placeholders, no ORM)
* **Database Tier:** PostgreSQL 18 on Neon Serverless Cloud (with SQLite development fallback for offline testing)
* **Presentation Tier:** HTML5, Tailwind CSS via CDN, vanilla JavaScript for dynamic passenger forms
* **WSGI Production Server:** Gunicorn with dynamic port resolution via `gunicorn.conf.py`

---

## Repository Structure

```text
mini-irctc/
├── app.py                      # Flask application routes, session auth, atomic booking and admin views
├── db.py                       # Database connection manager (PostgreSQL psycopg + local SQLite adapter)
├── gunicorn.conf.py            # Dynamic port binding configuration for Render deployment
├── Procfile                    # Web service startup command for cloud platforms
├── requirements.txt            # Python dependencies (Flask, psycopg, gunicorn, etc.)
├── test_app.py                 # Automated 12-test unit and integration test suite
├── sql/
│   ├── schema.sql              # DDL: 10 tables, integrity constraints, triggers, and mandatory VIEW
│   ├── seed.sql                # 12 stations, 16 trains, stops, classes, and initial demo data
│   └── demo_queries.sql        # Labeled SQL queries for viva examination
├── templates/                  # 11 Jinja2 HTML templates styled with Tailwind CSS
├── static/                     # Print stylesheet (print.css) and passenger form script (booking.js)
└── docs/                       # Conceptual Chen ER Diagram (.drawio and .svg)
```

---

## Local Installation and Execution

### 1. Clone Repository and Install Dependencies
```bash
git clone https://github.com/unclePRO/mini-irctc.git
cd mini-irctc
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
> **Offline Support:** If `DATABASE_URL` is not configured or PostgreSQL is unreachable, `db.py` automatically initializes and falls back to a zero-configuration local SQLite database (`railway_dev.db`).

### 3. Run Development Server
```bash
python app.py
```
Access the application at `http://127.0.0.1:5000` in any web browser.

### 4. Execute Test Suite
```bash
python test_app.py
```
Runs 12 automated integration tests verifying route ordering, password hashing, atomic booking transactions, pessimistic locking rollback, public PNR privacy, and SQL views.
