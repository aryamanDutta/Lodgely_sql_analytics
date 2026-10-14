from flask import Blueprint, render_template
from db.connection import query_all, query_one
import json

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
def index():
    # 1. Total number of bookings by status
    q1 = """
        SELECT booking_status, COUNT(*) AS total_bookings, COALESCE(SUM(total_amount), 0) AS total_value
        FROM BOOKING
        GROUP BY booking_status
        ORDER BY total_bookings DESC
    """
    bookings_by_status = query_all(q1)

    # 2. Total rooms by room type
    q2 = """
        SELECT room_type, COUNT(*) AS room_count, 
               MIN(price_per_night) AS min_price, 
               MAX(price_per_night) AS max_price, 
               AVG(price_per_night) AS avg_price
        FROM ROOM
        GROUP BY room_type
        ORDER BY room_count DESC
    """
    rooms_by_type = query_all(q2)

    # 3. Available rooms by hotel
    q3 = """
        SELECT h.hotel_id, h.hotel_name, h.location,
               COUNT(r.room_id) AS total_rooms,
               SUM(CASE WHEN r.room_status = 'Available' THEN 1 ELSE 0 END) AS available_rooms,
               SUM(CASE WHEN r.room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
               SUM(CASE WHEN r.room_status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_rooms
        FROM HOTEL h
        LEFT JOIN ROOM r ON h.hotel_id = r.hotel_id
        GROUP BY h.hotel_id, h.hotel_name, h.location
        ORDER BY h.hotel_name ASC
    """
    available_rooms_by_hotel = query_all(q3)

    # 4. Total recorded payments by payment method
    q4 = """
        SELECT payment_method, 
               COUNT(*) AS transaction_count, 
               COALESCE(SUM(amount), 0) AS total_amount,
               COALESCE(AVG(amount), 0) AS avg_amount
        FROM PAYMENT
        GROUP BY payment_method
        ORDER BY total_amount DESC
    """
    payments_by_method = query_all(q4)

    # 5. Payments grouped by payment status
    q5 = """
        SELECT payment_status, 
               COUNT(*) AS transaction_count, 
               COALESCE(SUM(amount), 0) AS total_amount
        FROM PAYMENT
        GROUP BY payment_status
        ORDER BY total_amount DESC
    """
    payments_by_status = query_all(q5)

    # 6. Booking count by hotel
    q6 = """
        SELECT h.hotel_name, 
               COUNT(b.booking_id) AS booking_count,
               COALESCE(SUM(b.total_amount), 0) AS total_booking_value
        FROM HOTEL h
        INNER JOIN ROOM r ON h.hotel_id = r.hotel_id
        INNER JOIN BOOKING b ON r.room_id = b.room_id
        GROUP BY h.hotel_id, h.hotel_name
        ORDER BY booking_count DESC
    """
    bookings_by_hotel = query_all(q6)

    # 7. Revenue collected by month (only Completed payments)
    q7 = """
        SELECT 
            DATE_FORMAT(payment_date, '%%Y-%%m') AS payment_month,
            COUNT(*) AS completed_transactions,
            COALESCE(SUM(amount), 0) AS total_revenue_collected
        FROM PAYMENT
        WHERE payment_status = 'Completed'
        GROUP BY DATE_FORMAT(payment_date, '%%Y-%%m')
        ORDER BY payment_month ASC
    """
    monthly_revenue = query_all(q7)

    # 8. Most frequently booked rooms
    q8 = """
        SELECT r.room_number, r.room_type, h.hotel_name, 
               COUNT(b.booking_id) AS total_bookings,
               COALESCE(SUM(b.total_amount), 0) AS total_revenue_generated
        FROM BOOKING b
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        GROUP BY r.room_id, r.room_number, r.room_type, h.hotel_name
        ORDER BY total_bookings DESC, total_revenue_generated DESC
        LIMIT 5
    """
    frequent_rooms = query_all(q8)

    # 9. Customers with highest number of bookings
    q9 = """
        SELECT c.customer_name, c.email, c.phone,
               COUNT(b.booking_id) AS bookings_count,
               COALESCE(SUM(b.total_amount), 0) AS total_spent
        FROM CUSTOMER c
        INNER JOIN BOOKING b ON c.customer_id = b.customer_id
        GROUP BY c.customer_id, c.customer_name, c.email, c.phone
        ORDER BY bookings_count DESC, total_spent DESC
        LIMIT 5
    """
    top_customers = query_all(q9)

    # 10. Average booking value overall & by room type
    q10_overall = query_one("""
        SELECT 
            COALESCE(AVG(total_amount), 0) AS avg_booking_value,
            COALESCE(MIN(total_amount), 0) AS min_booking_value,
            COALESCE(MAX(total_amount), 0) AS max_booking_value
        FROM BOOKING
    """) or {}

    q10_by_type = query_all("""
        SELECT r.room_type, 
               COUNT(b.booking_id) AS bookings_count,
               COALESCE(AVG(b.total_amount), 0) AS avg_booking_value
        FROM BOOKING b
        INNER JOIN ROOM r ON b.room_id = r.room_id
        GROUP BY r.room_type
        ORDER BY avg_booking_value DESC
    """)

    # 11. Room occupancy rate calculation
    # Formula: (Occupied Rooms / Total Rooms) * 100
    occupancy_data = query_one("""
        SELECT 
            COUNT(*) AS total_rooms,
            SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
            SUM(CASE WHEN room_status = 'Available' THEN 1 ELSE 0 END) AS available_rooms,
            SUM(CASE WHEN room_status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_rooms,
            ROUND((SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS occupancy_percentage
        FROM ROOM
    """) or {}

    # 12. Restaurant menu item counts by category
    q12 = """
        SELECT category, 
               COUNT(*) AS item_count, 
               MIN(price) AS min_price, 
               MAX(price) AS max_price, 
               AVG(price) AS avg_price
        FROM FOOD
        GROUP BY category
        ORDER BY item_count DESC
    """
    food_by_category = query_all(q12)

    # 13. Outstanding balances per booking (Unsettled Invoices)
    q13 = """
        SELECT 
            b.booking_id,
            c.customer_name,
            h.hotel_name,
            r.room_number,
            b.total_amount,
            COALESCE(paid.total_paid, 0) AS total_paid,
            (b.total_amount - COALESCE(paid.total_paid, 0)) AS balance_due,
            b.booking_status
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        LEFT JOIN (
            SELECT booking_id, SUM(amount) AS total_paid
            FROM PAYMENT
            WHERE payment_status = 'Completed'
            GROUP BY booking_id
        ) paid ON b.booking_id = paid.booking_id
        WHERE b.booking_status NOT IN ('Cancelled')
          AND (b.total_amount - COALESCE(paid.total_paid, 0)) > 0
        ORDER BY balance_due DESC
        LIMIT 10
    """
    outstanding_balances = query_all(q13)

    # 14. Housekeeping workload by staff member
    q14 = """
        SELECT 
            e.employee_name,
            e.designation,
            h.hotel_name,
            COUNT(hk.housekeeping_id) AS total_assignments,
            SUM(CASE WHEN hk.cleaning_status = 'Clean' THEN 1 ELSE 0 END) AS clean_rooms,
            SUM(CASE WHEN hk.cleaning_status = 'In Progress' THEN 1 ELSE 0 END) AS in_progress_rooms,
            SUM(CASE WHEN hk.cleaning_status = 'Dirty' THEN 1 ELSE 0 END) AS dirty_rooms
        FROM EMPLOYEE e
        INNER JOIN HOTEL h ON e.hotel_id = h.hotel_id
        LEFT JOIN HOUSEKEEPING hk ON e.employee_id = hk.employee_id
        WHERE e.designation = 'Housekeeper'
        GROUP BY e.employee_id, e.employee_name, e.designation, h.hotel_name
        ORDER BY total_assignments DESC
    """
    housekeeping_workload = query_all(q14)

    # Charts JSON serialization
    chart_hotel_names = [row['hotel_name'] for row in bookings_by_hotel]
    chart_hotel_counts = [row['booking_count'] for row in bookings_by_hotel]

    chart_month_labels = [row['payment_month'] for row in monthly_revenue]
    chart_month_revenue = [float(row['total_revenue_collected']) for row in monthly_revenue]

    chart_pay_methods = [row['payment_method'] for row in payments_by_method]
    chart_pay_amounts = [float(row['total_amount']) for row in payments_by_method]

    return render_template(
        'analytics.html',
        bookings_by_status=bookings_by_status,
        rooms_by_type=rooms_by_type,
        available_rooms_by_hotel=available_rooms_by_hotel,
        payments_by_method=payments_by_method,
        payments_by_status=payments_by_status,
        bookings_by_hotel=bookings_by_hotel,
        monthly_revenue=monthly_revenue,
        frequent_rooms=frequent_rooms,
        top_customers=top_customers,
        avg_overall=q10_overall,
        avg_by_type=q10_by_type,
        occupancy_data=occupancy_data,
        food_by_category=food_by_category,
        outstanding_balances=outstanding_balances,
        housekeeping_workload=housekeeping_workload,
        chart_hotel_names=json.dumps(chart_hotel_names),
        chart_hotel_counts=json.dumps(chart_hotel_counts),
        chart_month_labels=json.dumps(chart_month_labels),
        chart_month_revenue=json.dumps(chart_month_revenue),
        chart_pay_methods=json.dumps(chart_pay_methods),
        chart_pay_amounts=json.dumps(chart_pay_amounts)
    )
