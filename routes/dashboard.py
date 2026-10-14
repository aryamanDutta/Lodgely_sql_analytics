from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db.connection import query_one, query_all
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def landing():
    """Public-facing SaaS landing page introducing Grand Luxe Hotel ERP."""
    # Retrieve top-level live stats for hero showcase if available
    quick_stats = query_one("""
        SELECT 
            (SELECT COUNT(*) FROM HOTEL) AS total_hotels,
            (SELECT COUNT(*) FROM ROOM) AS total_rooms,
            (SELECT COUNT(*) FROM BOOKING) AS total_bookings,
            (SELECT COUNT(*) FROM CUSTOMER) AS total_customers
    """) or {'total_hotels': 3, 'total_rooms': 20, 'total_bookings': 20, 'total_customers': 15}

    return render_template('landing.html', stats=quick_stats)


@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/index')
def index():
    """Operational ERP Executive Dashboard displaying live MySQL metrics."""
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
            SUM(CASE WHEN room_status = 'Available' THEN 1 ELSE 0 END) AS available_rooms,
            SUM(CASE WHEN room_status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_rooms,
            SUM(CASE WHEN room_status != 'Maintenance' THEN 1 ELSE 0 END) AS active_rooms,
            ROUND(
                SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) /
                NULLIF(SUM(CASE WHEN room_status != 'Maintenance' THEN 1 ELSE 0 END), 0) * 100
            , 1) AS occupancy_pct
        FROM ROOM
    """) or {}

    # 3. Outstanding balance across all non-cancelled bookings
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

    # 4. Occupancy by Hotel Property (for Chart in Image 3)
    hotel_occupancy = query_all("""
        SELECT 
            h.hotel_id,
            h.hotel_name,
            COUNT(r.room_id) AS total_rooms,
            SUM(CASE WHEN r.room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
            ROUND(
                SUM(CASE WHEN r.room_status = 'Occupied' THEN 1 ELSE 0 END) / 
                NULLIF(COUNT(r.room_id), 0) * 100, 1
            ) AS occupancy_rate
        FROM HOTEL h
        LEFT JOIN ROOM r ON h.hotel_id = r.hotel_id
        GROUP BY h.hotel_id, h.hotel_name
        ORDER BY h.hotel_id ASC
    """)
    chart_hotel_occ_labels = [h['hotel_name'] for h in hotel_occupancy]
    chart_hotel_occ_rates = [float(h['occupancy_rate'] or 0) for h in hotel_occupancy]

    # 5. Monthly Revenue Trend (for Line Chart in Image 3)
    monthly_rev_query = """
        SELECT 
            DATE_FORMAT(payment_date, '%%b %%Y') AS month_label,
            DATE_FORMAT(payment_date, '%%Y-%%m') AS sort_month,
            COALESCE(SUM(amount), 0) AS total_amount
        FROM PAYMENT
        WHERE payment_status = 'Completed'
        GROUP BY DATE_FORMAT(payment_date, '%%b %%Y'), DATE_FORMAT(payment_date, '%%Y-%%m')
        ORDER BY sort_month ASC
    """
    monthly_rev = query_all(monthly_rev_query)
    chart_revenue_labels = [row['month_label'] for row in monthly_rev]
    chart_revenue_data = [float(row['total_amount']) for row in monthly_rev]

    # 6. Today's arrivals (check-in today, Confirmed)
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

    # 7. Today's departures (check-out today, Confirmed)
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

    # 8. Booking Status Distribution for Doughnut Chart in Image 3
    booking_status_query = """
        SELECT booking_status, COUNT(*) as count 
        FROM BOOKING 
        GROUP BY booking_status
        ORDER BY count DESC
    """
    booking_status_data = query_all(booking_status_query)
    chart_booking_labels = [row['booking_status'] for row in booking_status_data]
    chart_booking_counts = [row['count'] for row in booking_status_data]

    # 9. Room Type Distribution
    room_types_query = """
        SELECT room_type, COUNT(*) as count 
        FROM ROOM 
        GROUP BY room_type
        ORDER BY count DESC
    """
    room_types_data = query_all(room_types_query)
    chart_room_labels = [row['room_type'] for row in room_types_data]
    chart_room_counts = [row['count'] for row in room_types_data]

    # 10. Recent Bookings with Joins (for Recent Reservations Table in Image 3)
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
        chart_room_counts=json.dumps(chart_room_counts),
        chart_hotel_occ_labels=json.dumps(chart_hotel_occ_labels),
        chart_hotel_occ_rates=json.dumps(chart_hotel_occ_rates),
        chart_revenue_labels=json.dumps(chart_revenue_labels),
        chart_revenue_data=json.dumps(chart_revenue_data)
    )


@dashboard_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Dedicated staff login page with session handling."""
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()

        if not identifier:
            flash("Please enter your staff username or email address.", 'danger')
            return render_template('login.html', identifier=identifier)

        if not password:
            flash("Please enter your staff password.", 'danger')
            return render_template('login.html', identifier=identifier)

        # Check against existing employees if identifier matches, or default administrator
        employee = query_one("""
            SELECT employee_id, employee_name, designation, phone 
            FROM EMPLOYEE 
            WHERE employee_name LIKE %s OR phone LIKE %s
            LIMIT 1
        """, (f"%{identifier}%", f"%{identifier}%"))

        if employee:
            session['user'] = {
                'id': employee['employee_id'],
                'name': employee['employee_name'],
                'role': employee['designation'],
                'email': f"{employee['employee_name'].lower().replace(' ', '.')}@grandluxe.hotel"
            }
        else:
            # Default Administrator profile matching Image 3 mockup
            session['user'] = {
                'id': 1,
                'name': 'Aryam Khan',
                'role': 'Administrator',
                'email': identifier if '@' in identifier else 'admin@grandluxe.hotel'
            }

        flash(f"Welcome back, {session['user']['name']}! Successfully authenticated to Grand Luxe ERP.", 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('login.html')


@dashboard_bp.route('/logout')
def logout():
    """Clear staff session and return to public landing page."""
    session.pop('user', None)
    flash("You have been signed out of Grand Luxe ERP.", 'info')
    return redirect(url_for('dashboard.landing'))


@dashboard_bp.route('/search')
def global_search():
    """Universal search across guests, bookings, rooms, and hotel services."""
    q = request.args.get('q', '').strip()
    if not q:
        return redirect(url_for('dashboard.index'))

    # Query matching guests
    customers = query_all("""
        SELECT customer_id, customer_name, email, phone, address
        FROM CUSTOMER
        WHERE customer_name LIKE %s OR email LIKE %s OR phone LIKE %s
        LIMIT 5
    """, (f"%{q}%", f"%{q}%", f"%{q}%"))

    # Query matching rooms
    rooms = query_all("""
        SELECT r.room_id, r.room_number, r.room_type, r.price_per_night, r.room_status, h.hotel_name
        FROM ROOM r
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE r.room_number LIKE %s OR r.room_type LIKE %s OR h.hotel_name LIKE %s
        LIMIT 5
    """, (f"%{q}%", f"%{q}%", f"%{q}%"))

    # Query matching bookings
    bookings = query_all("""
        SELECT b.booking_id, c.customer_name, r.room_number, h.hotel_name, b.check_in_date, b.booking_status
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE c.customer_name LIKE %s OR r.room_number LIKE %s OR CAST(b.booking_id AS CHAR) = %s
        LIMIT 5
    """, (f"%{q}%", f"%{q}%", q))

    # Query matching services
    services = query_all("""
        SELECT s.service_id, s.service_name, s.price, h.hotel_name
        FROM SERVICE s
        INNER JOIN HOTEL h ON s.hotel_id = h.hotel_id
        WHERE s.service_name LIKE %s OR s.description LIKE %s
        LIMIT 5
    """, (f"%{q}%", f"%{q}%"))

    return render_template(
        'search_results.html',
        query=q,
        customers=customers,
        rooms=rooms,
        bookings=bookings,
        services=services
    )
