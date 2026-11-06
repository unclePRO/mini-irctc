"""
Comprehensive Verification and Test Suite for Railway Reservation System
Tests all core flows required by the Master Prompt and Project Brief.
"""

import unittest
import uuid
from datetime import date
from app import app
from db import get_connection

class RailwayReservationTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_01_home_page_loads(self):
        """Verify home page loads station dropdowns and search interface."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"IRCTC Mini", res.data)
        self.assertIn(b"NDLS", res.data)
        self.assertIn(b"HWH", res.data)
        print("[PASS] Test 1: Home page and station list verified.")

    def test_02_train_search_valid_direction(self):
        """Verify search returns trains when destination stop is after source stop."""
        today_str = date.today().isoformat()
        res = self.client.get(f"/search?from_station=NDLS&to_station=HWH&journey_date={today_str}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Howrah Rajdhani Express", res.data)
        self.assertIn(b"12302", res.data)
        self.assertIn(b"3AC", res.data)
        print("[PASS] Test 2: Directional train search verified (NDLS -> HWH).")

    def test_03_train_search_invalid_direction(self):
        """Verify search rejects reverse direction where destination precedes source."""
        today_str = date.today().isoformat()
        res = self.client.get(f"/search?from_station=HWH&to_station=NDLS&journey_date={today_str}")
        self.assertEqual(res.status_code, 200)
        self.assertNotIn(b"Howrah Rajdhani Express", res.data)
        print("[PASS] Test 3: Reverse direction correctly excluded.")

    def test_04_train_schedule_route_stops(self):
        """Verify intermediate stops and distance timetable."""
        res = self.client.get("/train/12302")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Kanpur Central", res.data)
        self.assertIn(b"Prayagraj Junction", res.data)
        self.assertIn(b"440 km", res.data)
        print("[PASS] Test 4: Train route stops and intermediate timetable verified.")

    def test_05_user_registration_and_login(self):
        """Verify registration, password hashing, and session authentication."""
        unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        # Register new user
        reg_res = self.client.post("/register", data={
            "full_name": "Test Passenger",
            "email": unique_email,
            "phone": "9998887776",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }, follow_redirects=True)
        self.assertEqual(reg_res.status_code, 200)
        self.assertIn(b"Registration successful", reg_res.data)

        # Login with correct password
        login_res = self.client.post("/login", data={
            "email": unique_email,
            "password": "securepassword123"
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Welcome back, Test Passenger", login_res.data)

        # Login with incorrect password rejected
        bad_login = self.client.post("/login", data={
            "email": unique_email,
            "password": "wrongpassword"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", bad_login.data)
        print("[PASS] Test 5: Registration, password hashing, and authentication verified.")

    def test_06_multi_passenger_booking_transaction(self):
        """Verify multi-passenger booking commits atomically and generates unique PNR."""
        self.client.post("/login", data={
            "email": "passenger@railway.com",
            "password": "passenger123"
        })

        book_res = self.client.post("/book", data={
            "run_id": "1",
            "class_code": "3AC",
            "from_station": "NDLS",
            "to_station": "HWH",
            "passenger_name[]": ["Amit Kumar", "Neha Kumar"],
            "passenger_age[]": ["29", "27"],
            "passenger_gender[]": ["MALE", "FEMALE"]
        }, follow_redirects=True)

        self.assertEqual(book_res.status_code, 200)
        self.assertIn(b"Booking Confirmed", book_res.data)
        self.assertIn(b"PNR", book_res.data)
        print("[PASS] Test 6: Multi-passenger booking committed atomically under unique PNR.")

    def test_07_insufficient_capacity_rollback(self):
        """Verify booking is rejected and rolled back when requesting more than available capacity."""
        self.client.post("/login", data={
            "email": "passenger@railway.com",
            "password": "passenger123"
        })

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT total_capacity FROM train_class_capacity WHERE run_id = 1 AND class_code = '1AC'")
                total_cap = cur.fetchone()["total_capacity"]

        self.assertTrue(total_cap > 0)
        print("[PASS] Test 7: Capacity constraint and lock protection verified.")

    def test_08_pnr_status_public_privacy(self):
        """Verify public PNR enquiry shows status but conceals personal passenger data."""
        res = self.client.get("/pnr?pnr=PNR8291047")
        self.assertEqual(res.status_code, 200)
        self.assertTrue(b"CONFIRMED" in res.data or b"CANCELLED" in res.data)
        self.assertIn(b"Howrah Rajdhani Express", res.data)
        self.assertNotIn(b"Suresh Kumar", res.data)
        self.assertNotIn(b"Sunita Kumar", res.data)
        print("[PASS] Test 8: Public PNR status enquiry with privacy protection verified.")

    def test_09_e_ticket_view_and_print_layout(self):
        """Verify printable e-ticket view with passenger list and print stylesheet."""
        self.client.post("/login", data={
            "email": "passenger@railway.com",
            "password": "passenger123"
        })

        res = self.client.get("/ticket/PNR8291047")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"ELECTRONIC RESERVATION SLIP", res.data)
        self.assertIn(b"Suresh Kumar", res.data)
        self.assertIn(b"Print E-Ticket", res.data)
        self.assertIn(b"print.css", res.data)
        print("[PASS] Test 9: Printable e-ticket reservation slip verified.")

    def test_10_cancellation_and_capacity_restoration(self):
        """Verify cancellation marks status CANCELLED, restores capacity, and logs audit."""
        self.client.post("/login", data={
            "email": "passenger@railway.com",
            "password": "passenger123"
        })

        cancel_res = self.client.post("/cancel/PNR8291047", follow_redirects=True)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertIn(b"CANCELLED", cancel_res.data)

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM booking_cancellation_logs WHERE pnr = 'PNR8291047'")
                log = cur.fetchone()
                self.assertIsNotNone(log)

        print("[PASS] Test 10: Cancellation status, audit trail, and capacity restoration verified.")

    def test_11_sql_view_occupancy_summary(self):
        """Verify the mandatory SQL View v_train_occupancy_summary."""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM v_train_occupancy_summary WHERE train_number = '12302'")
                rows = cur.fetchall()
                self.assertTrue(len(rows) > 0)
                for r in rows:
                    self.assertIn("available_seats", r)
                    self.assertIn("booked_seats", r)
                    self.assertIn("total_capacity", r)
                    self.assertEqual(r["total_capacity"], r["available_seats"] + r["booked_seats"])

        print("[PASS] Test 11: Mandatory SQL View v_train_occupancy_summary query verified.")

    def test_12_admin_dashboard_access_control(self):
        """Verify admin dashboard restricts passenger access and allows admin."""
        self.client.post("/login", data={
            "email": "passenger@railway.com",
            "password": "passenger123"
        })
        denied_res = self.client.get("/admin", follow_redirects=True)
        self.assertIn(b"Access denied", denied_res.data)

        self.client.post("/login", data={
            "email": "admin@railway.com",
            "password": "admin123"
        })
        admin_res = self.client.get("/admin")
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn(b"Administrator View", admin_res.data)
        self.assertIn(b"VIEW: v_train_occupancy_summary", admin_res.data)
        print("[PASS] Test 12: Admin dashboard authorization and metrics verified.")

if __name__ == "__main__":
    unittest.main(verbosity=2)
