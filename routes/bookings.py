from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from datetime import datetime, date
from db.connection import query_all, query_one, execute_commit, transaction_context

bookings_bp = Blueprint('bookings', __name__, url_prefix='/bookings')

@bookings_bp.route('/')
def list_bookings():
    booking_id = request.args.get('booking_id', '').strip()
    customer_name = request.args.get('customer_name', '').strip()
    hotel_id = request.args.get('hotel_id', '').strip()
    booking_status = request.args.get('booking_status', '').strip()
    check_in_from = request.args.get('check_in_from', '').strip()
    check_in_to = request.args.get('check_in_to', '').strip()

    base_query = """
        SELECT 
            b.booking_id,
            b.customer_id,
            c.customer_name,
            c.email AS customer_email,
            r.room_number,
            r.room_type,
            r.room_status,
            h.hotel_id,
            h.hotel_name,
            b.check_in_date,
            b.check_out_date,
            b.number_of_guests,
            b.booking_status,
            b.total_amount,
            COALESCE((SELECT SUM(amount) FROM PAYMENT WHERE booking_id = b.booking_id AND payment_status = 'Completed'), 0) AS total_paid
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE 1=1
    """
    params = []

    if booking_id and booking_id.isdigit():
        base_query += " AND b.booking_id = %s"
        params.append(int(booking_id))

    if customer_name:
        base_query += " AND c.customer_name LIKE %s"
        params.append(f"%{customer_name}%")

    if hotel_id and hotel_id.isdigit():
        base_query += " AND h.hotel_id = %s"
        params.append(int(hotel_id))

    if booking_status:
        base_query += " AND b.booking_status = %s"
        params.append(booking_status)

    if check_in_from:
        base_query += " AND b.check_in_date >= %s"
        params.append(check_in_from)

    if check_in_to:
        base_query += " AND b.check_in_date <= %s"
        params.append(check_in_to)

    base_query += " ORDER BY b.booking_id DESC"

    bookings = query_all(base_query, tuple(params))
    hotels = query_all("SELECT hotel_id, hotel_name FROM HOTEL ORDER BY hotel_name ASC")

    return render_template(
        'bookings.html',
        bookings=bookings,
        hotels=hotels,
        filters={
            'booking_id': booking_id,
            'customer_name': customer_name,
            'hotel_id': hotel_id,
            'booking_status': booking_status,
            'check_in_from': check_in_from,
            'check_in_to': check_in_to
        }
    )

@bookings_bp.route('/<int:booking_id>')
def booking_detail(booking_id):
    booking_query = """
        SELECT 
            b.booking_id,
            b.customer_id,
            c.customer_name,
            c.email AS customer_email,
            c.phone AS customer_phone,
            c.address AS customer_address,
            r.room_id,
            r.room_number,
            r.room_type,
            r.room_status,
            r.price_per_night,
            h.hotel_id,
            h.hotel_name,
            h.location AS hotel_location,
            h.star_rating,
            b.check_in_date,
            b.check_out_date,
            b.number_of_guests,
            b.booking_status,
            b.total_amount,
            b.created_at
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE b.booking_id = %s
    """
    booking = query_one(booking_query, (booking_id,))
    if not booking:
        abort(404)

    payments_query = """
        SELECT payment_id, payment_date, amount, payment_method, payment_status
        FROM PAYMENT
        WHERE booking_id = %s
        ORDER BY payment_date DESC
    """
    payments = query_all(payments_query, (booking_id,))

    # Compute financial balances
    total_paid = sum(float(p['amount']) for p in payments if p['payment_status'] == 'Completed')
    total_amount = float(booking['total_amount'])
    balance_due = max(0.0, total_amount - total_paid)

    payment_summary = {
        'total_paid': total_paid,
        'balance_due': balance_due,
        'is_fully_paid': (balance_due == 0.0 and total_amount > 0),
        'is_partially_paid': (0 < total_paid < total_amount),
        'is_unpaid': (total_paid == 0.0 and total_amount > 0)
    }

    return render_template(
        'booking_detail.html',
        booking=booking,
        payments=payments,
        financials=payment_summary
    )

@bookings_bp.route('/new', methods=['GET', 'POST'])
def new_booking():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', '').strip()
        room_id = request.form.get('room_id', '').strip()
        check_in_str = request.form.get('check_in_date', '').strip()
        check_out_str = request.form.get('check_out_date', '').strip()
        guests_str = request.form.get('number_of_guests', '1').strip()
        booking_status = request.form.get('booking_status', 'Confirmed').strip()

        errors = []
        if not (customer_id and customer_id.isdigit()):
            errors.append("Please select a valid customer.")
        if not (room_id and room_id.isdigit()):
            errors.append("Please select a valid room.")

        check_in_date = None
        check_out_date = None
        try:
            check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            if check_out_date <= check_in_date:
                errors.append("Check-out date must be strictly after check-in date.")
        except (ValueError, TypeError):
            errors.append("Valid check-in and check-out dates are required (YYYY-MM-DD).")

        try:
            guests = int(guests_str)
            if guests < 1:
                errors.append("Number of guests must be at least 1.")
        except ValueError:
            errors.append("Number of guests must be a valid integer.")
            guests = 1

        if not errors:
            try:
                with transaction_context() as cursor:
                    # 1. Lock room row with FOR UPDATE to prevent race conditions
                    cursor.execute(
                        "SELECT room_id, price_per_night, room_status FROM ROOM WHERE room_id = %s FOR UPDATE",
                        (int(room_id),)
                    )
                    room = cursor.fetchone()
                    if not room:
                        errors.append("Selected room does not exist.")
                    elif room['room_status'] == 'Maintenance':
                        errors.append("Selected room is currently undergoing maintenance.")
                    else:
                        # 2. Check overlap with active bookings with lock
                        cursor.execute("""
                            SELECT COUNT(*) as overlap_count
                            FROM BOOKING
                            WHERE room_id = %s
                              AND booking_status IN ('Confirmed', 'Completed')
                              AND check_in_date < %s
                              AND check_out_date > %s
                            FOR UPDATE
                        """, (int(room_id), check_out_str, check_in_str))
                        overlap = cursor.fetchone()
                        if overlap and overlap['overlap_count'] > 0:
                            errors.append("Selected room is already booked for the chosen date range.")

                    if not errors:
                        nights = (check_out_date - check_in_date).days
                        total_amount = float(room['price_per_night']) * max(1, nights)

                        # 3. Insert booking
                        cursor.execute("""
                            INSERT INTO BOOKING (customer_id, room_id, check_in_date, check_out_date, number_of_guests, booking_status, total_amount)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            int(customer_id),
                            int(room_id),
                            check_in_str,
                            check_out_str,
                            guests,
                            booking_status,
                            total_amount
                        ))
                        new_id = cursor.lastrowid

                        # 4. If booking starts today and is confirmed, mark room occupied
                        today = date.today()
                        if check_in_date <= today < check_out_date and booking_status == 'Confirmed':
                            cursor.execute(
                                "UPDATE ROOM SET room_status = 'Occupied' WHERE room_id = %s AND room_status != 'Maintenance'",
                                (int(room_id),)
                            )

                        flash(f"Booking #{new_id} successfully created! Total: ₹{total_amount:,.2f} for {nights} night(s).", 'success')
                        return redirect(url_for('bookings.booking_detail', booking_id=new_id))

            except Exception as e:
                errors.append(f"Database error creating reservation: {str(e)}")

        # If errors occurred, preserve input and redisplay
        for error in errors:
            flash(error, 'danger')
        customers = query_all("SELECT customer_id, customer_name, email FROM CUSTOMER ORDER BY customer_name ASC")
        rooms = query_all("""
            SELECT r.room_id, r.room_number, r.room_type, r.price_per_night, h.hotel_name
            FROM ROOM r
            INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
            WHERE r.room_status != 'Maintenance'
            ORDER BY h.hotel_name, r.room_number ASC
        """)
        return render_template(
            'booking_new.html',
            customers=customers,
            rooms=rooms,
            form_data=request.form
        )

    # GET request
    customers = query_all("SELECT customer_id, customer_name, email FROM CUSTOMER ORDER BY customer_name ASC")
    rooms = query_all("""
        SELECT r.room_id, r.room_number, r.room_type, r.price_per_night, h.hotel_name
        FROM ROOM r
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE r.room_status != 'Maintenance'
        ORDER BY h.hotel_name, r.room_number ASC
    """)
    return render_template('booking_new.html', customers=customers, rooms=rooms, form_data={})

@bookings_bp.route('/<int:booking_id>/edit', methods=['GET', 'POST'])
def edit_booking(booking_id):
    booking = query_one("""
        SELECT b.*, r.hotel_id 
        FROM BOOKING b
        INNER JOIN ROOM r ON b.room_id = r.room_id
        WHERE b.booking_id = %s
    """, (booking_id,))
    if not booking:
        abort(404)

    if booking['booking_status'] in ('Completed', 'Cancelled'):
        flash(f"Booking #{booking_id} is {booking['booking_status']} and cannot be edited.", 'warning')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    if request.method == 'POST':
        room_id = request.form.get('room_id', '').strip()
        check_in_str = request.form.get('check_in_date', '').strip()
        check_out_str = request.form.get('check_out_date', '').strip()
        guests_str = request.form.get('number_of_guests', '1').strip()
        booking_status = request.form.get('booking_status', booking['booking_status']).strip()

        errors = []
        if not (room_id and room_id.isdigit()):
            errors.append("Please select a valid room.")

        check_in_date = None
        check_out_date = None
        try:
            check_in_date = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out_str, '%Y-%m-%d').date()
            if check_out_date <= check_in_date:
                errors.append("Check-out date must be strictly after check-in date.")
        except (ValueError, TypeError):
            errors.append("Valid check-in and check-out dates are required (YYYY-MM-DD).")

        try:
            guests = int(guests_str)
            if guests < 1:
                errors.append("Number of guests must be at least 1.")
        except ValueError:
            errors.append("Number of guests must be a valid integer.")
            guests = 1

        if not errors:
            try:
                with transaction_context() as cursor:
                    # 1. Lock room
                    cursor.execute(
                        "SELECT room_id, price_per_night, room_status FROM ROOM WHERE room_id = %s FOR UPDATE",
                        (int(room_id),)
                    )
                    room = cursor.fetchone()
                    if not room:
                        errors.append("Selected room does not exist.")
                    elif room['room_status'] == 'Maintenance' and int(room_id) != booking['room_id']:
                        errors.append("Selected room is currently undergoing maintenance.")
                    else:
                        # 2. Check overlap excluding this booking_id
                        cursor.execute("""
                            SELECT COUNT(*) as overlap_count
                            FROM BOOKING
                            WHERE room_id = %s
                              AND booking_id != %s
                              AND booking_status IN ('Confirmed', 'Completed')
                              AND check_in_date < %s
                              AND check_out_date > %s
                            FOR UPDATE
                        """, (int(room_id), booking_id, check_out_str, check_in_str))
                        overlap = cursor.fetchone()
                        if overlap and overlap['overlap_count'] > 0:
                            errors.append("Selected room is already booked for the chosen date range.")

                    if not errors:
                        nights = (check_out_date - check_in_date).days
                        new_total = float(room['price_per_night']) * max(1, nights)

                        # Update booking record
                        cursor.execute("""
                            UPDATE BOOKING
                            SET room_id = %s,
                                check_in_date = %s,
                                check_out_date = %s,
                                number_of_guests = %s,
                                booking_status = %s,
                                total_amount = %s
                            WHERE booking_id = %s
                        """, (
                            int(room_id),
                            check_in_str,
                            check_out_str,
                            guests,
                            booking_status,
                            new_total,
                            booking_id
                        ))

                        flash(f"Booking #{booking_id} updated successfully! New Total: ₹{new_total:,.2f} ({nights} nights).", 'success')
                        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

            except Exception as e:
                errors.append(f"Error updating booking: {str(e)}")

        for error in errors:
            flash(error, 'danger')

    rooms = query_all("""
        SELECT r.room_id, r.room_number, r.room_type, r.price_per_night, h.hotel_name
        FROM ROOM r
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        ORDER BY h.hotel_name, r.room_number ASC
    """)
    customer = query_one("SELECT customer_name, email FROM CUSTOMER WHERE customer_id = %s", (booking['customer_id'],))
    return render_template(
        'booking_edit.html',
        booking=booking,
        customer=customer,
        rooms=rooms
    )

@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    booking = query_one("SELECT booking_id, room_id, booking_status FROM BOOKING WHERE booking_id = %s", (booking_id,))
    if not booking:
        abort(404)

    if booking['booking_status'] in ('Cancelled', 'Completed'):
        flash(f"Booking #{booking_id} is already {booking['booking_status']}.", 'info')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    with transaction_context() as cursor:
        cursor.execute("UPDATE BOOKING SET booking_status = 'Cancelled' WHERE booking_id = %s", (booking_id,))
        # If the room was currently Occupied, check if any other active reservation for today exists
        cursor.execute("""
            SELECT COUNT(*) AS active_count
            FROM BOOKING
            WHERE room_id = %s
              AND booking_status = 'Confirmed'
              AND check_in_date <= CURDATE()
              AND check_out_date > CURDATE()
        """, (booking['room_id'],))
        active = cursor.fetchone()
        if not active or active['active_count'] == 0:
            cursor.execute(
                "UPDATE ROOM SET room_status = 'Available' WHERE room_id = %s AND room_status = 'Occupied'",
                (booking['room_id'],)
            )

    flash(f"Booking #{booking_id} has been cancelled successfully. Room availability updated.", 'success')
    return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

@bookings_bp.route('/<int:booking_id>/check-in', methods=['POST'])
def check_in(booking_id):
    booking = query_one("""
        SELECT b.booking_id, b.room_id, b.booking_status, r.room_status, r.room_number
        FROM BOOKING b
        INNER JOIN ROOM r ON b.room_id = r.room_id
        WHERE b.booking_id = %s
    """, (booking_id,))
    if not booking:
        abort(404)

    if booking['booking_status'] == 'Cancelled':
        flash("Cannot check in a cancelled booking.", 'danger')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    if booking['booking_status'] == 'Completed':
        flash("This booking is already completed.", 'info')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    if booking['room_status'] == 'Maintenance':
        flash(f"Room {booking['room_number']} is currently under maintenance. Please reassign the room before check-in.", 'danger')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    with transaction_context() as cursor:
        cursor.execute("UPDATE BOOKING SET booking_status = 'Confirmed' WHERE booking_id = %s", (booking_id,))
        cursor.execute("UPDATE ROOM SET room_status = 'Occupied' WHERE room_id = %s", (booking['room_id'],))

    flash(f"Guest checked into Room {booking['room_number']}. Room status set to 'Occupied'.", 'success')
    return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

@bookings_bp.route('/<int:booking_id>/check-out', methods=['POST'])
def check_out(booking_id):
    booking = query_one("""
        SELECT b.booking_id, b.room_id, b.booking_status, b.total_amount, r.hotel_id, r.room_number, r.room_status,
               COALESCE((SELECT SUM(amount) FROM PAYMENT WHERE booking_id = b.booking_id AND payment_status = 'Completed'), 0) AS total_paid
        FROM BOOKING b
        INNER JOIN ROOM r ON b.room_id = r.room_id
        WHERE b.booking_id = %s
    """, (booking_id,))
    if not booking:
        abort(404)

    if booking['booking_status'] == 'Completed':
        flash("This booking has already been checked out.", 'info')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    unpaid_balance = float(booking['total_amount']) - float(booking['total_paid'])
    if unpaid_balance > 0:
        flash(f"Notice: Guest checked out with an unsettled balance of ₹{unpaid_balance:,.2f}.", 'warning')

    with transaction_context() as cursor:
        # Mark booking completed
        cursor.execute("UPDATE BOOKING SET booking_status = 'Completed' WHERE booking_id = %s", (booking_id,))
        # Mark room available
        cursor.execute("UPDATE ROOM SET room_status = 'Available' WHERE room_id = %s AND room_status != 'Maintenance'", (booking['room_id'],))
        # Find housekeeper for this hotel and create a dirty inspection record
        cursor.execute("SELECT employee_id FROM EMPLOYEE WHERE designation = 'Housekeeper' AND hotel_id = %s LIMIT 1", (booking['hotel_id'],))
        housekeeper = cursor.fetchone()
        emp_id = housekeeper['employee_id'] if housekeeper else 3 # fallback to housekeeper 3
        cursor.execute("""
            INSERT INTO HOUSEKEEPING (employee_id, room_id, cleaning_date, cleaning_status)
            VALUES (%s, %s, CURDATE(), 'Dirty')
        """, (emp_id, booking['room_id']))

    flash(f"Booking #{booking_id} checked out. Room {booking['room_number']} marked Available and scheduled for housekeeping.", 'success')
    return redirect(url_for('bookings.booking_detail', booking_id=booking_id))
