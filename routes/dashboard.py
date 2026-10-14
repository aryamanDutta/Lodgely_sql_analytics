from flask import Blueprint, render_template
from db.connection import query_one, query_all
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    # 1. Summary Cards Queries
    stats_query = """
    SELECT 
        (SELECT COUNT(*) FROM HOTEL) AS total_hotels,
        (SELECT COUNT(*) FROM ROOM) AS total_rooms,
        (SELECT COUNT(*) FROM ROOM WHERE room_status = 'Available') AS available_rooms,
        (SELECT COUNT(*) FROM ROOM WHERE room_status = 'Occupied') AS occupied_rooms,
        (SELECT COUNT(*) FROM CUSTOMER) AS total_customers,
        (SELECT COUNT(*) FROM BOOKING) AS total_bookings,
        (SELECT COUNT(*) FROM BOOKING WHERE booking_status = 'Confirmed') AS confirmed_bookings,
        (SELECT COALESCE(SUM(amount), 0) FROM PAYMENT WHERE payment_status = 'Completed') AS total_revenue,
        (SELECT COALESCE(SUM(amount), 0) FROM PAYMENT WHERE payment_status = 'Pending') AS pending_amount,
        (SELECT COUNT(*) FROM PAYMENT WHERE payment_status = 'Pending') AS pending_count
    """
    stats = query_one(stats_query) or {}

    # 2. Occupancy rate (non-maintenance rooms only)
    occupancy = query_one("""
        SELECT
            COUNT(*) AS total_rooms,
            SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
            SUM(CASE WHEN room_status != 'Maintenance' THEN 1 ELSE 0 END) AS active_rooms,
            ROUND(
                SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) /
                NULLIF(SUM(CASE WHEN room_status != 'Maintenance' THEN 1 ELSE 0 END), 0) * 100
            , 1) AS occupancy_pct
        FROM ROOM
    """) or {}

    # 3. Outstanding balance across all non-cancelled bookings
    # Use a JOIN-based approach compatible with MySQL ONLY_FULL_GROUP_BY
    outstanding = query_one("""
        SELECT
            COUNT(DISTINCT b.booking_id) AS bookings_with_balance,
            COALESCE(SUM(b.total_amount - COALESCE(paid.paid_amount, 0)), 0) AS total_outstanding
        FROM BOOKING b
        LEFT JOIN (
            SELECT booking_id, SUM(amount) AS paid_amount
            FROM PAYMENT
            WHERE payment_status = 'Completed'
            GROUP BY booking_id
        ) paid ON b.booking_id = paid.booking_id
        WHERE b.booking_status NOT IN ('Cancelled')
          AND b.total_amount > COALESCE(paid.paid_amount, 0)
    """) or {}

    # 4. Today's arrivals (check-in today, Confirmed)
    todays_arrivals = query_all("""
        SELECT b.booking_id, c.customer_name, r.room_number, r.room_type, h.hotel_name,
               b.check_in_date, b.check_out_date, b.number_of_guests
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE b.check_in_date = CURDATE() AND b.booking_status = 'Confirmed'
        ORDER BY b.booking_id ASC
        LIMIT 8
    """)

    # 5. Today's departures (check-out today, Confirmed)
    todays_departures = query_all("""
        SELECT b.booking_id, c.customer_name, r.room_number, r.room_type, h.hotel_name,
               b.check_in_date, b.check_out_date, b.number_of_guests, b.total_amount
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE b.check_out_date = CURDATE() AND b.booking_status = 'Confirmed'
        ORDER BY b.booking_id ASC
        LIMIT 8
    """)

    # 6. Booking Status Distribution for Chart
    booking_status_query = """
        SELECT booking_status, COUNT(*) as count 
        FROM BOOKING 
        GROUP BY booking_status
        ORDER BY count DESC
    """
    booking_status_data = query_all(booking_status_query)
    chart_booking_labels = [row['booking_status'] for row in booking_status_data]
    chart_booking_counts = [row['count'] for row in booking_status_data]

    # 7. Room Type Distribution for Chart
    room_types_query = """
        SELECT room_type, COUNT(*) as count 
        FROM ROOM 
        GROUP BY room_type
        ORDER BY count DESC
    """
    room_types_data = query_all(room_types_query)
    chart_room_labels = [row['room_type'] for row in room_types_data]
    chart_room_counts = [row['count'] for row in room_types_data]

    # 8. Recent Bookings with Joins
    recent_bookings_query = """
        SELECT 
            b.booking_id,
            c.customer_name,
            c.email AS customer_email,
            r.room_number,
            r.room_type,
            h.hotel_name,
            b.check_in_date,
            b.check_out_date,
            b.number_of_guests,
            b.booking_status,
            b.total_amount
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        ORDER BY b.booking_id DESC
        LIMIT 6
    """
    recent_bookings = query_all(recent_bookings_query)

    return render_template(
        'dashboard.html',
        stats=stats,
        occupancy=occupancy,
        outstanding=outstanding,
        todays_arrivals=todays_arrivals,
        todays_departures=todays_departures,
        recent_bookings=recent_bookings,
        chart_booking_labels=json.dumps(chart_booking_labels),
        chart_booking_counts=json.dumps(chart_booking_counts),
        chart_room_labels=json.dumps(chart_room_labels),
        chart_room_counts=json.dumps(chart_room_counts)
    )
