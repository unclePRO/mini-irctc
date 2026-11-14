# 🚆 Railway Reservation System (IRCTC Mini)

> A full-stack, concurrency-safe Railway Reservation System built for a second-year B.Tech Database Management Systems (DBMS) course project. Engineered with direct parameterized SQL (no ORM), strict Boyce-Codd Normal Form (BCNF) relational schema, ACID transactions, and live cloud deployment.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render-00c7b7?style=for-the-badge&logo=render&logoColor=white)](https://mini-irctc.onrender.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2018-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![Python](https://img.shields.io/badge/Backend-Python%203.13%20%2F%20Flask-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://flask.palletsprojects.com/)
[![TailwindCSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

---

## 🌐 Live Deployment & Demo

* **Live Web App:** [https://mini-irctc.onrender.com/](https://mini-irctc.onrender.com/)
* **Database:** Neon Serverless PostgreSQL 18 (AWS `ap-southeast-1`)
* **Hosting:** Render Web Service with Gunicorn WSGI

### 🔑 Pre-Configured Test Accounts

| Role | Email | Password | Access & Features |
| :--- | :--- | :--- | :--- |
| **Passenger Demo** | `passenger@railway.com` | `passenger123` | Search trains, book 1–6 passengers, view printable e-tickets, cancel bookings |
| **Administrator Demo** | `admin@railway.com` | `admin123` | Admin dashboard, live SQL VIEW occupancy monitoring, trigger audit logs |

**Sample Demonstration PNRs:**
* `PNR1029384`: Active confirmed booking on 12952 (Mumbai Rajdhani)
* `PNR4829102`: Cancelled booking (demonstrates cancellation status & trigger audit trail)

---

## ✨ Key Features & DBMS Concepts

* **Directional Route Validation:** Validates intermediate station sequence numbers (`stop_sequence(from) < stop_sequence(to)`). Rejects reverse-direction travel.
* **Concurrency-Safe Atomic Bookings:** Uses pessimistic row-level locking (`SELECT ... FOR UPDATE`) on class capacity to prevent overbooking race conditions.
* **Mandatory SQL View (`v_train_occupancy_summary`):** Encapsulates multi-table joins and real-time seat accounting for live admin operations.
* **Automated Audit Trigger (`trg_booking_cancellation`):** Automatically logs cancellation events, restores available capacity, and preserves booking history.
* **Public PNR Enquiry with Privacy Protection:** Conceals private passenger names from public searches while displaying confirmed itinerary status.
* **Printable Electronic Reservation Slip (ERS):** Print-ready e-ticket styling via `@media print` CSS rules.
* **Normalized Relational Schema (BCNF):** 10 relations systematically derived via the 7-step ER-to-relational mapping algorithm, all verified in Boyce-Codd Normal Form.

---

## 🛠️ Technology Stack

* **Backend:** Python 3.13, Flask (server-rendered Jinja2 templates, session auth with Scrypt password hashing)
* **Database Driver:** `psycopg 3` executing direct parameterized SQL queries (`%s` placeholders, **NO ORM**)
* **Frontend:** HTML5, Tailwind CSS (via CDN), vanilla JavaScript (dynamic passenger row handling and live fare calculation)
* **Production Server:** Gunicorn WSGI container on Render

---

## 📁 Repository Structure

```text
mini-irctc/
├── app.py                      # Flask routes, session auth, atomic booking & admin views
├── db.py                       # Database connection manager (PostgreSQL + local SQLite fallback)
├── gunicorn.conf.py            # Dynamic port binding for Render deployment
├── Procfile                    # Web service startup command for cloud deployment
├── requirements.txt            # Python dependencies (Flask, psycopg, gunicorn, etc.)
├── test_app.py                 # Automated 12-test unit & integration test suite
├── sql/
│   ├── schema.sql              # DDL: 10 tables, constraints, trigger, and mandatory SQL VIEW
│   ├── seed.sql                # 12 stations, 16 trains, stops, classes, and initial demo users
│   └── demo_queries.sql        # Labeled SQL queries for viva examination
├── templates/                  # 11 Jinja2 HTML templates styled with Tailwind CSS
├── static/                     # Print stylesheet (print.css) and passenger form script (booking.js)
└── docs/                       # Conceptual Chen ER Diagram (.drawio and .svg)
```

---

## 🚀 Quick Local Setup

### 1. Clone & Install
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
> **Offline Ready:** If `DATABASE_URL` is unset or PostgreSQL is unreachable, `db.py` automatically initializes and connects to a zero-configuration local SQLite database (`railway_dev.db`).

### 3. Run Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your web browser.

### 4. Run Automated Tests
```bash
python test_app.py
```
Runs 12 integration tests verifying routing, authentication, multi-passenger transactions, capacity locks, and SQL views.

---

## 👥 Course & Team Information

* **Course Code:** 25CS2004 — Database Systems Design
* **Group:** Group No. 19

| Name | Roll Number |
| :--- | :--- |
| Bachireddy Sreenikesh Reddy | CS25B2051 |
| Aviral Pandey | CS25B2054 |
| Vikramaditya | CS25I1069 |
