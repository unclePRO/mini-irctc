# Railway Reservation System (IRCTC Mini)

A simplified, full-stack Railway Reservation System built for a second-year B.Tech Database Management Systems (DBMS) course project. The application emphasizes correct Entity-Relationship (ER) modeling, conversion to relations, functional dependency and normalization analysis (BCNF/3NF), raw parameterized SQL queries, database constraints, concurrent transactions, and an interactive server-rendered web application.

---

## 1. Technology Stack

- **Backend**: Python 3.13 / Flask (server-rendered routes and HTML forms, no separate REST API or ORM)
- **Frontend**: HTML5, Tailwind CSS (via CDN), vanilla JavaScript (dynamic passenger rows and live fare calculation), and Jinja2 templates
- **Database Engine**: PostgreSQL (connected via `psycopg` direct parameterized SQL; includes zero-dependency local SQLite development adapter for offline work)
- **Production Server**: Gunicorn (configured for Render or cloud Linux hosting)
- **Conceptual Modeling**: Chen ER notation (`.drawio` editable XML and `.svg` export)

---

## 2. Directory Structure

```text
dbms_project/
├── app.py                      # Flask routes, authentication, booking transaction & admin handlers
├── db.py                       # Database connection manager (PostgreSQL psycopg + local development adapter)
├── requirements.txt            # Python dependencies (Flask, psycopg, python-dotenv, gunicorn)
├── .env.example                # Example environment configuration
├── .gitignore                  # Git exclusions for secrets, virtual environments, and temporary files
├── test_app.py                 # Automated unit and integration test suite covering all core requirements
├── sql/
│   ├── schema.sql              # DDL: CREATE TABLE, integrity constraints, triggers, and mandatory VIEW
│   ├── seed.sql                # Realistic fictional demonstration data for Indian Railways
│   └── demo_queries.sql        # Executable SQL queries for viva demonstration (JOINs, GROUP BY, subqueries)
├── docs/
│   ├── Railway_Reservation_ER_Diagram.drawio  # Editable diagrams.net / draw.io XML file
│   └── ER_Diagram.svg          # High-resolution vector export of the ER Conceptual Model
├── templates/
│   ├── base.html               # Master layout with Tailwind styling and navigation
│   ├── index.html              # Search interface with station selectors and date picker
│   ├── search_results.html     # Directional route search results with live availability and fares
│   ├── train_schedule.html     # Ordered train stops timetable
│   ├── book.html               # Multi-passenger reservation form with dynamic vanilla JS rows
│   ├── booking_confirmed.html  # Atomic transaction confirmation with assigned PNR
│   ├── ticket.html             # Printable electronic reservation slip (ERS) with print stylesheet
│   ├── pnr_status.html         # Public PNR enquiry with privacy protection
│   ├── history.html            # User booking history and cancellation actions
│   ├── login.html              # User authentication sign-in
│   ├── register.html           # Passenger account registration
│   └── admin.html              # Administrator dashboard querying mandatory SQL VIEW
├── static/
│   ├── css/
│   │   └── print.css           # Clean print-friendly CSS for e-tickets (@media print)
│   └── js/
│       └── booking.js          # Dynamic passenger field addition/removal and fare preview
└── references/                 # Professor-provided reference slides and project brief
```

---

## 3. Core Database & Modeling Assumptions

1. **Route Ordering**:
   A train defines an ordered sequence of station stops in the `train_stops` weak entity. An origin-to-destination search is valid only when the destination occurs strictly **after** the origin in sequence order (`ts_from.stop_sequence < ts_to.stop_sequence`).
2. **Train Runs & Capacity**:
   A `train_run` models a train operating on a specific calendar date. Confirmed passengers occupy one unit of class capacity for the entire run. Availability is calculated dynamically from `train_class_capacity.total_capacity` minus active `CONFIRMED` passenger reservations.
3. **No Seat/Berth Assignment**:
   Per project brief simplifications, tickets are reserved as general capacity units per class. Physical berth numbers, Tatkal, RAC, and waiting lists are deliberately omitted.
4. **Concurrency & Atomicity**:
   Ticket bookings run inside an explicit transaction using PostgreSQL row-level locks (`SELECT ... FOR UPDATE`) on the target class capacity row. Overbooking requests are rejected and rolled back immediately.
5. **Cancellation Policy**:
   Cancelling an authorized reservation updates `booking_status` to `'CANCELLED'`. The record is preserved for auditing, and reserved capacity is restored to the seat pool. A database trigger (`trg_booking_cancellation`) automatically logs the cancellation into `booking_cancellation_logs`.

---

## 4. Local Setup and Run Instructions (Windows)

### Step 1: Clone or Open Workspace
Open a PowerShell terminal in the project directory:
```powershell
cd d:\dbms_project
```

### Step 2: Install Python Dependencies
```powershell
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Edit `.env` to configure your settings:
```ini
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/railway_db
SECRET_KEY=my-super-secret-course-project-key
FLASK_DEBUG=True
PORT=5000
```
> **Note for Local Offline Testing**: If PostgreSQL is not yet started on your computer, `db.py` automatically initializes and connects to a zero-configuration local SQLite development database (`railway_dev.db`). When your PostgreSQL server is running, the application will natively connect via `psycopg`.

### Step 4: Initialize the Database (Optional / Manual Reset)
To initialize and seed the database at any time:
```powershell
python db.py init
```

### Step 5: Start the Web Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 5. Running the Test Suite

Run the automated test suite to verify all core flows (search, booking, concurrency check, cancellation, view queries):
```powershell
python test_app.py
```

---

## 6. Pre-Configured Test Accounts

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@railway.com` | `admin123` | Full access, Admin Dashboard, SQL VIEW monitoring |
| **Passenger** | `passenger@railway.com` | `passenger123` | Search, Book, View E-Ticket, Cancel Bookings |
| **Passenger** | `rahul@gmail.com` | `rahul123` | Search, Book, Personal history |
| **Passenger** | `priya@gmail.com` | `priya123` | Search, Book, Personal history |

**Sample Demonstration PNRs**:
- `PNR8291047`: Confirmed booking on 12302 (NDLS → HWH, 3AC)
- `PNR4829102`: Cancelled booking (demonstrates cancellation status & audit trigger log)

---

## 7. Public Deployment Guide (Render)

This application is ready to deploy on [Render](https://render.com) using standard environment variables:

1. **Push to GitHub**:
   Initialize git and push the repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Railway Reservation System"
   git remote add origin https://github.com/<your-username>/railway-reservation.git
   git push -u origin main
   ```
2. **Create PostgreSQL Database on Render**:
   - Go to [dashboard.render.com](https://dashboard.render.com) and click **New +** → **PostgreSQL**.
   - Copy the **Internal Database URL** (or External URL).
3. **Initialize Remote Schema**:
   Connect via `psql` or run `python db.py init` with `DATABASE_URL` pointing to your Render PostgreSQL instance.
4. **Create Web Service on Render**:
   - Click **New +** → **Web Service** and select your GitHub repository.
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Environment Variables**:
     - `DATABASE_URL`: Your Render PostgreSQL connection URL.
     - `SECRET_KEY`: A random secure string.
     - `PYTHON_VERSION`: `3.13.0`
5. **Free-Tier Notice**:
   Render free web services spin down after 15 minutes of inactivity and take ~50 seconds to restart on the first incoming request. Free Render PostgreSQL databases expire after 30 days; always keep `sql/schema.sql` and `sql/seed.sql` in version control to re-seed if needed.
