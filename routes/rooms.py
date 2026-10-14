from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from datetime import datetime
from db.connection import query_all, query_one, execute_commit

rooms_bp = Blueprint('rooms', __name__, url_prefix='/rooms')

VALID_ROOM_TYPES = ['Single', 'Double', 'Deluxe', 'Suite', 'Presidential Suite']
VALID_ROOM_STATUSES = ['Available', 'Occupied', 'Maintenance']

@rooms_bp.route('/')
def list_rooms():
    # Read search and filter parameters
    room_number = request.args.get('room_number', '').strip()
    hotel_id = request.args.get('hotel_id', '').strip()
    room_type = request.args.get('room_type', '').strip()
    room_status = request.args.get('room_status', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    avail_check_in = request.args.get('avail_check_in', '').strip()
    avail_check_out = request.args.get('avail_check_out', '').strip()
    sort_by = request.args.get('sort_by', 'room_number').strip()
    order = request.args.get('order', 'asc').strip().lower()

    # Safelist sorting parameters to prevent SQL injection
    valid_sort_columns = {
        'room_number': 'r.room_number',
        'price': 'r.price_per_night',
        'hotel': 'h.hotel_name',
        'type': 'r.room_type',
        'status': 'r.room_status'
    }
    sort_column = valid_sort_columns.get(sort_by, 'r.room_number')
    sort_direction = 'DESC' if order == 'desc' else 'ASC'

    # Build parameterized query
    base_query = """
        SELECT 
            r.room_id,
            r.room_number,
            r.room_type,
            r.price_per_night,
            r.room_status,
            h.hotel_id,
            h.hotel_name,
            h.location,
            h.star_rating
        FROM ROOM r
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE 1=1
    """
    params = []

    if room_number:
        base_query += " AND r.room_number LIKE %s"
        params.append(f"%{room_number}%")

    if hotel_id and hotel_id.isdigit():
        base_query += " AND r.hotel_id = %s"
        params.append(int(hotel_id))

    if room_type:
        base_query += " AND r.room_type = %s"
        params.append(room_type)

    if room_status:
        base_query += " AND r.room_status = %s"
        params.append(room_status)

    if min_price:
        try:
            base_query += " AND r.price_per_night >= %s"
            params.append(float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            base_query += " AND r.price_per_night <= %s"
            params.append(float(max_price))
        except ValueError:
            pass

    # Date-based availability filter using real reservation data
    if avail_check_in and avail_check_out:
        try:
            d_in = datetime.strptime(avail_check_in, '%Y-%m-%d').date()
            d_out = datetime.strptime(avail_check_out, '%Y-%m-%d').date()
            if d_out > d_in:
                base_query += """
                    AND r.room_status != 'Maintenance'
                    AND r.room_id NOT IN (
                        SELECT b.room_id 
                        FROM BOOKING b 
                        WHERE b.booking_status IN ('Confirmed', 'Completed')
                          AND b.check_in_date < %s 
                          AND b.check_out_date > %s
                    )
                """
                params.extend([avail_check_out, avail_check_in])
            else:
                flash("Availability filter: Check-out date must be after check-in date.", 'warning')
        except ValueError:
            pass

    base_query += f" ORDER BY {sort_column} {sort_direction}"

    rooms = query_all(base_query, tuple(params))

    # Metadata for dropdowns
    hotels = query_all("SELECT hotel_id, hotel_name FROM HOTEL ORDER BY hotel_name ASC")
    room_types = query_all("SELECT DISTINCT room_type FROM ROOM ORDER BY room_type ASC")

    return render_template(
        'rooms.html',
        rooms=rooms,
        hotels=hotels,
        room_types=room_types,
        filters={
            'room_number': room_number,
            'hotel_id': hotel_id,
            'room_type': room_type,
            'room_status': room_status,
            'min_price': min_price,
            'max_price': max_price,
            'avail_check_in': avail_check_in,
            'avail_check_out': avail_check_out,
            'sort_by': sort_by,
            'order': order
        }
    )

@rooms_bp.route('/new', methods=['GET', 'POST'])
def new_room():
    hotels = query_all("SELECT hotel_id, hotel_name FROM HOTEL ORDER BY hotel_name ASC")

    if request.method == 'POST':
        hotel_id = request.form.get('hotel_id', '').strip()
        room_number = request.form.get('room_number', '').strip()
        room_type = request.form.get('room_type', '').strip()
        price_str = request.form.get('price_per_night', '').strip()
        room_status = request.form.get('room_status', 'Available').strip()

        errors = []
        if not (hotel_id and hotel_id.isdigit()):
            errors.append("Please select a valid hotel property.")
        if not room_number:
            errors.append("Room number is required.")
        if room_type not in VALID_ROOM_TYPES:
            errors.append(f"Room type must be one of: {', '.join(VALID_ROOM_TYPES)}")
        if room_status not in VALID_ROOM_STATUSES:
            errors.append(f"Room status must be one of: {', '.join(VALID_ROOM_STATUSES)}")

        price = 0.0
        try:
            price = float(price_str)
            if price <= 0:
                errors.append("Nightly price must be greater than zero.")
        except ValueError:
            errors.append("A valid positive numeric price is required.")

        # Check unique room number per hotel
        if hotel_id and room_number:
            existing = query_one(
                "SELECT room_id FROM ROOM WHERE hotel_id = %s AND room_number = %s",
                (int(hotel_id), room_number)
            )
            if existing:
                errors.append(f"Room '{room_number}' already exists in the selected hotel property.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('room_new.html', hotels=hotels, form_data=request.form, room_types=VALID_ROOM_TYPES, room_statuses=VALID_ROOM_STATUSES)

        sql = """
            INSERT INTO ROOM (hotel_id, room_number, room_type, price_per_night, room_status)
            VALUES (%s, %s, %s, %s, %s)
        """
        new_id = execute_commit(sql, (int(hotel_id), room_number, room_type, price, room_status))
        flash(f"Room #{room_number} added successfully to inventory (ID: #{new_id})!", 'success')
        return redirect(url_for('rooms.list_rooms', hotel_id=hotel_id))

    return render_template('room_new.html', hotels=hotels, form_data={}, room_types=VALID_ROOM_TYPES, room_statuses=VALID_ROOM_STATUSES)

@rooms_bp.route('/<int:room_id>/edit', methods=['GET', 'POST'])
def edit_room(room_id):
    room = query_one("""
        SELECT r.*, h.hotel_name 
        FROM ROOM r 
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id 
        WHERE r.room_id = %s
    """, (room_id,))
    if not room:
        abort(404)

    if request.method == 'POST':
        room_number = request.form.get('room_number', '').strip()
        room_type = request.form.get('room_type', '').strip()
        price_str = request.form.get('price_per_night', '').strip()
        room_status = request.form.get('room_status', '').strip()

        errors = []
        if not room_number:
            errors.append("Room number is required.")
        if room_type not in VALID_ROOM_TYPES:
            errors.append("Invalid room type.")
        if room_status not in VALID_ROOM_STATUSES:
            errors.append("Invalid room status.")

        try:
            price = float(price_str)
            if price <= 0:
                errors.append("Price per night must be positive.")
        except ValueError:
            errors.append("Valid numeric price is required.")

        # Check unique room number in same hotel
        existing = query_one(
            "SELECT room_id FROM ROOM WHERE hotel_id = %s AND room_number = %s AND room_id != %s",
            (room['hotel_id'], room_number, room_id)
        )
        if existing:
            errors.append(f"Room '{room_number}' already exists in this hotel.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('room_edit.html', room=room, form_data=request.form, room_types=VALID_ROOM_TYPES, room_statuses=VALID_ROOM_STATUSES)

        sql = """
            UPDATE ROOM
            SET room_number = %s, room_type = %s, price_per_night = %s, room_status = %s
            WHERE room_id = %s
        """
        execute_commit(sql, (room_number, room_type, price, room_status, room_id))
        flash(f"Room '{room_number}' updated successfully!", 'success')
        return redirect(url_for('rooms.list_rooms', hotel_id=room['hotel_id']))

    return render_template('room_edit.html', room=room, form_data=room, room_types=VALID_ROOM_TYPES, room_statuses=VALID_ROOM_STATUSES)

@rooms_bp.route('/<int:room_id>/delete', methods=['POST'])
def delete_room(room_id):
    room = query_one("SELECT room_number, hotel_id FROM ROOM WHERE room_id = %s", (room_id,))
    if not room:
        abort(404)

    # Check for active or past bookings referencing this room
    ref_check = query_one("SELECT COUNT(*) AS booking_count FROM BOOKING WHERE room_id = %s", (room_id,))
    if ref_check and ref_check['booking_count'] > 0:
        flash(
            f"Cannot delete Room '{room['room_number']}': Room has {ref_check['booking_count']} reservation record(s). Change status to 'Maintenance' instead to preserve audit history.",
            'danger'
        )
        return redirect(url_for('rooms.list_rooms', hotel_id=room['hotel_id']))

    execute_commit("DELETE FROM ROOM WHERE room_id = %s", (room_id,))
    flash(f"Room '{room['room_number']}' has been deleted from inventory.", 'success')
    return redirect(url_for('rooms.list_rooms'))
