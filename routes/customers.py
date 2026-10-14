from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
import re
from db.connection import query_all, query_one, execute_commit

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')

def validate_customer_data(name, email, phone, address, exclude_id=None):
    """Validate customer inputs and ensure email uniqueness."""
    errors = []
    if not name or len(name) < 2:
        errors.append("Customer full name is required (minimum 2 characters).")
    if not email or '@' not in email or '.' not in email:
        errors.append("A valid email address is required.")
    if not phone or len(phone) < 7:
        errors.append("A valid contact phone number is required.")
    if not address or len(address) < 3:
        errors.append("A valid address/city is required.")

    # Email uniqueness check
    if email:
        sql = "SELECT customer_id FROM CUSTOMER WHERE email = %s"
        params = [email]
        if exclude_id:
            sql += " AND customer_id != %s"
            params.append(exclude_id)
        existing = query_one(sql, tuple(params))
        if existing:
            errors.append(f"The email '{email}' is already registered to another customer.")

    return errors

@customers_bp.route('/')
def list_customers():
    name = request.args.get('name', '').strip()
    email = request.args.get('email', '').strip()
    phone = request.args.get('phone', '').strip()

    base_query = """
        SELECT 
            c.customer_id,
            c.customer_name,
            c.email,
            c.phone,
            c.address,
            COUNT(b.booking_id) AS total_bookings,
            COALESCE(SUM(CASE WHEN b.booking_status IN ('Confirmed', 'Completed') THEN b.total_amount ELSE 0 END), 0) AS total_spent
        FROM CUSTOMER c
        LEFT JOIN BOOKING b ON c.customer_id = b.customer_id
        WHERE 1=1
    """
    params = []

    if name:
        base_query += " AND c.customer_name LIKE %s"
        params.append(f"%{name}%")

    if email:
        base_query += " AND c.email LIKE %s"
        params.append(f"%{email}%")

    if phone:
        base_query += " AND c.phone LIKE %s"
        params.append(f"%{phone}%")

    base_query += " GROUP BY c.customer_id, c.customer_name, c.email, c.phone, c.address ORDER BY c.customer_name ASC"

    customers = query_all(base_query, tuple(params))

    return render_template(
        'customers.html',
        customers=customers,
        filters={'name': name, 'email': email, 'phone': phone}
    )

@customers_bp.route('/<int:customer_id>')
def customer_detail(customer_id):
    customer = query_one("""
        SELECT customer_id, customer_name, email, phone, address, created_at 
        FROM CUSTOMER 
        WHERE customer_id = %s
    """, (customer_id,))

    if not customer:
        abort(404)

    bookings = query_all("""
        SELECT 
            b.booking_id,
            b.check_in_date,
            b.check_out_date,
            b.number_of_guests,
            b.booking_status,
            b.total_amount,
            r.room_number,
            r.room_type,
            h.hotel_name
        FROM BOOKING b
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE b.customer_id = %s
        ORDER BY b.booking_id DESC
    """, (customer_id,))

    return render_template('customer_detail.html', customer=customer, bookings=bookings)

@customers_bp.route('/new', methods=['GET', 'POST'])
def new_customer():
    if request.method == 'POST':
        name = request.form.get('customer_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        errors = validate_customer_data(name, email, phone, address)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('customer_new.html', form_data=request.form)

        sql = """
            INSERT INTO CUSTOMER (customer_name, email, phone, address)
            VALUES (%s, %s, %s, %s)
        """
        new_id = execute_commit(sql, (name, email, phone, address))
        flash(f"Customer profile for '{name}' created successfully (ID: #{new_id})!", 'success')
        return redirect(url_for('customers.customer_detail', customer_id=new_id))

    return render_template('customer_new.html', form_data={})

@customers_bp.route('/<int:customer_id>/edit', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = query_one("SELECT * FROM CUSTOMER WHERE customer_id = %s", (customer_id,))
    if not customer:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('customer_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()

        errors = validate_customer_data(name, email, phone, address, exclude_id=customer_id)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('customer_edit.html', customer=customer, form_data=request.form)

        sql = """
            UPDATE CUSTOMER 
            SET customer_name = %s, email = %s, phone = %s, address = %s
            WHERE customer_id = %s
        """
        execute_commit(sql, (name, email, phone, address, customer_id))
        flash(f"Customer profile #{customer_id} updated successfully!", 'success')
        return redirect(url_for('customers.customer_detail', customer_id=customer_id))

    return render_template('customer_edit.html', customer=customer, form_data=customer)

@customers_bp.route('/<int:customer_id>/delete', methods=['POST'])
def delete_customer(customer_id):
    customer = query_one("SELECT customer_name FROM CUSTOMER WHERE customer_id = %s", (customer_id,))
    if not customer:
        abort(404)

    # Referential Integrity Check: ensure customer has no bookings
    ref_check = query_one("SELECT COUNT(*) AS booking_count FROM BOOKING WHERE customer_id = %s", (customer_id,))
    if ref_check and ref_check['booking_count'] > 0:
        flash(
            f"Cannot delete guest '{customer['customer_name']}': Guest has {ref_check['booking_count']} reservation record(s) on file. Record must be retained for auditing.",
            'danger'
        )
        return redirect(url_for('customers.customer_detail', customer_id=customer_id))

    execute_commit("DELETE FROM CUSTOMER WHERE customer_id = %s", (customer_id,))
    flash(f"Customer #{customer_id} ('{customer['customer_name']}') successfully deleted.", 'success')
    return redirect(url_for('customers.list_customers'))
