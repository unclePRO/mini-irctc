-- ============================================================================
-- RAILWAY RESERVATION SYSTEM (DBMS COURSE PROJECT)
-- File: sql/demo_queries.sql
-- Description: Demonstrable, executable SQL queries aligned with SQL_Chapter_DB_1.pptx
--              for viva inspection, testing, and report verification.
-- ============================================================================

-- ============================================================================
-- TOPIC 1: BASIC SELECT, FILTERING, ALIASES & ORDER BY (Slides 50-98)
-- Retrieve all scheduled train services ordered by journey date and train number.
-- ============================================================================
SELECT 
    tr.run_id,
    tr.train_number,
    t.train_name,
    tr.journey_date,
    tr.status AS run_status
FROM train_runs tr
JOIN trains t ON tr.train_number = t.train_number
WHERE tr.status = 'SCHEDULED' AND tr.journey_date >= CURRENT_DATE
ORDER BY tr.journey_date ASC, tr.train_number ASC;


-- ============================================================================
-- TOPIC 2: MULTI-TABLE INNER JOIN (Slides 99-129)
-- Route timetable: Show the complete ordered journey stops for Rajdhani (12302)
-- ============================================================================
SELECT 
    t.train_number,
    t.train_name,
    ts.stop_sequence,
    s.station_code,
    s.station_name,
    s.city,
    COALESCE(TO_CHAR(ts.arrival_time, 'HH24:MI'), 'ORIGIN') AS arrival,
    COALESCE(TO_CHAR(ts.departure_time, 'HH24:MI'), 'DESTINATION') AS departure,
    ts.halt_minutes,
    ts.distance_km
FROM trains t
JOIN train_stops ts ON t.train_number = ts.train_number
JOIN stations s ON ts.station_code = s.station_code
WHERE t.train_number = '12302'
ORDER BY ts.stop_sequence ASC;


-- ============================================================================
-- TOPIC 3: LEFT OUTER JOIN (Slides 110-125)
-- List all stations and the count of trains originating there, including
-- stations with zero originating trains.
-- ============================================================================
SELECT 
    s.station_code,
    s.station_name,
    s.city,
    COUNT(t.train_number) AS originating_trains_count
FROM stations s
LEFT JOIN trains t ON s.station_code = t.source_station_code
GROUP BY s.station_code, s.station_name, s.city
ORDER BY originating_trains_count DESC, s.station_code ASC;


-- ============================================================================
-- TOPIC 4: AGGREGATES WITH GROUP BY & HAVING (Slides 130-178)
-- Calculate total confirmed tickets, total passengers, and gross revenue
-- per travel class, displaying only classes with total revenue > 1000.
-- ============================================================================
SELECT 
    tc.class_code,
    tc.class_name,
    COUNT(DISTINCT b.booking_id) AS total_confirmed_bookings,
    COUNT(bp.passenger_seq) AS total_passengers_carried,
    COALESCE(SUM(b.total_fare), 0.00) AS total_revenue
FROM travel_classes tc
JOIN bookings b ON tc.class_code = b.class_code AND b.booking_status = 'CONFIRMED'
JOIN booking_passengers bp ON b.booking_id = bp.booking_id
GROUP BY tc.class_code, tc.class_name
HAVING SUM(b.total_fare) > 1000.00
ORDER BY total_revenue DESC;


-- ============================================================================
-- TOPIC 5: NESTED SUBQUERY WITH 'IN' (Slides 183-194)
-- Find all train names and numbers that have runs scheduled today.
-- ============================================================================
SELECT train_number, train_name
FROM trains
WHERE train_number IN (
    SELECT train_number
    FROM train_runs
    WHERE journey_date = CURRENT_DATE AND status = 'SCHEDULED'
);


-- ============================================================================
-- TOPIC 6: SCALAR SUBQUERY IN WHERE CLAUSE (Slides 179-182)
-- Find bookings whose total fare is strictly greater than the average booking fare.
-- ============================================================================
SELECT 
    b.pnr,
    u.full_name AS booked_by,
    b.total_fare,
    b.booking_status
FROM bookings b
JOIN users u ON b.user_id = u.user_id
WHERE b.total_fare > (
    SELECT AVG(total_fare) FROM bookings
);


-- ============================================================================
-- TOPIC 7: CORRELATED SUBQUERY WITH 'EXISTS' (Slides 195-214)
-- Find all registered users who have booked at least one ticket.
-- ============================================================================
SELECT u.user_id, u.full_name, u.email, u.phone
FROM users u
WHERE EXISTS (
    SELECT 1 
    FROM bookings b 
    WHERE b.user_id = u.user_id
);


-- ============================================================================
-- TOPIC 8: CORRELATED SUBQUERY WITH 'NOT EXISTS' (Slides 195-214)
-- Find users who have active confirmed bookings but have NEVER cancelled any booking.
-- ============================================================================
SELECT u.user_id, u.full_name, u.email
FROM users u
WHERE EXISTS (
    SELECT 1 FROM bookings b WHERE b.user_id = u.user_id AND b.booking_status = 'CONFIRMED'
)
AND NOT EXISTS (
    SELECT 1 FROM bookings b WHERE b.user_id = u.user_id AND b.booking_status = 'CANCELLED'
);


-- ============================================================================
-- TOPIC 9: QUERYING THE MANDATORY SQL VIEW (Slides 219-235)
-- Query v_train_occupancy_summary for trains that have available seats.
-- ============================================================================
SELECT 
    train_number,
    train_name,
    journey_date,
    class_code,
    class_name,
    total_capacity,
    booked_seats,
    available_seats,
    base_fare
FROM v_train_occupancy_summary
WHERE journey_date >= CURRENT_DATE AND available_seats > 0
ORDER BY journey_date ASC, train_number ASC, base_fare ASC;


-- ============================================================================
-- TOPIC 10: OPTIONAL WINDOW FUNCTION - DENSE_RANK() (Viva Demonstration)
-- Rank travel classes by popularity (number of passengers booked).
-- ============================================================================
SELECT 
    tc.class_code,
    tc.class_name,
    COUNT(bp.passenger_seq) AS passengers_count,
    DENSE_RANK() OVER (ORDER BY COUNT(bp.passenger_seq) DESC) AS popularity_rank
FROM travel_classes tc
LEFT JOIN bookings b ON tc.class_code = b.class_code AND b.booking_status = 'CONFIRMED'
LEFT JOIN booking_passengers bp ON b.booking_id = bp.booking_id
GROUP BY tc.class_code, tc.class_name
ORDER BY popularity_rank ASC;


-- ============================================================================
-- TOPIC 11: OPTIONAL TRIGGER VERIFICATION (Slides 236-240)
-- Inspect the cancellation audit log table populated by trigger trg_booking_cancellation.
-- ============================================================================
SELECT 
    log_id,
    booking_id,
    pnr,
    cancelled_at,
    cancellation_reason
FROM booking_cancellation_logs
ORDER BY cancelled_at DESC;
