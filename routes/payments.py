from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from datetime import datetime, date
from db.connection import query_all, query_one, execute_commit
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

payments_bp = Blueprint('payments', __name__, url_prefix='/payments')

@payments_bp.route('/')
def list_payments():
    payment_status = request.args.get('payment_status', '').strip()
    payment_method = request.args.get('payment_method', '').strip()
    booking_id = request.args.get('booking_id', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    base_query = """
        SELECT 
            p.payment_id,
            p.booking_id,
            p.payment_date,
            p.amount,
            p.payment_method,
            p.payment_status,
            c.customer_name,
            h.hotel_name
        FROM PAYMENT p
        INNER JOIN BOOKING b ON p.booking_id = b.booking_id
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE 1=1
    """
    params = []

    if payment_status:
        base_query += " AND p.payment_status = %s"
        params.append(payment_status)

    if payment_method:
        base_query += " AND p.payment_method = %s"
        params.append(payment_method)

    if booking_id and booking_id.isdigit():
        base_query += " AND p.booking_id = %s"
        params.append(int(booking_id))

    if date_from:
        base_query += " AND DATE(p.payment_date) >= %s"
        params.append(date_from)

    if date_to:
        base_query += " AND DATE(p.payment_date) <= %s"
        params.append(date_to)

    base_query += " ORDER BY p.payment_date DESC"

    payments = query_all(base_query, tuple(params))

    # Aggregated Summary Queries from MySQL
    summary_stats = query_one("""
        SELECT 
            COALESCE(SUM(CASE WHEN payment_status = 'Completed' THEN amount ELSE 0 END), 0) AS total_collected,
            COALESCE(SUM(CASE WHEN payment_status = 'Pending' THEN amount ELSE 0 END), 0) AS total_pending,
            COALESCE(SUM(CASE WHEN payment_status = 'Failed' THEN amount ELSE 0 END), 0) AS total_failed,
            COALESCE(SUM(CASE WHEN payment_status = 'Refunded' THEN amount ELSE 0 END), 0) AS total_refunded,
            COUNT(*) AS total_transactions
        FROM PAYMENT
    """) or {}

    method_breakdown = query_all("""
        SELECT 
            payment_method,
            COUNT(*) AS transaction_count,
            COALESCE(SUM(amount), 0) AS total_amount
        FROM PAYMENT
        GROUP BY payment_method
        ORDER BY total_amount DESC
    """)

    payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash']
    payment_statuses = ['Completed', 'Pending', 'Failed', 'Refunded']

    return render_template(
        'payments.html',
        payments=payments,
        summary=summary_stats,
        method_breakdown=method_breakdown,
        payment_methods=payment_methods,
        payment_statuses=payment_statuses,
        filters={
            'payment_status': payment_status,
            'payment_method': payment_method,
            'booking_id': booking_id,
            'date_from': date_from,
            'date_to': date_to
        }
    )


VALID_PAYMENT_METHODS = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash']
VALID_PAYMENT_STATUSES_FORM = ['Completed', 'Pending', 'Failed', 'Refunded']


@payments_bp.route('/new', methods=['GET', 'POST'])
def new_payment():
    """Record a payment against an existing booking. Prevents overpayment."""
    booking_id_raw = request.args.get('booking_id', '') if request.method == 'GET' \
                     else request.form.get('booking_id', '')

    if not booking_id_raw or not str(booking_id_raw).isdigit():
        flash("A valid booking ID is required to record a payment.", 'danger')
        return redirect(url_for('payments.list_payments'))

    booking_id = int(booking_id_raw)

    booking = query_one("""
        SELECT b.booking_id, b.booking_status, b.total_amount,
               c.customer_name, c.email AS customer_email,
               r.room_number, r.room_type, h.hotel_name
        FROM BOOKING b
        INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
        INNER JOIN ROOM r ON b.room_id = r.room_id
        INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
        WHERE b.booking_id = %s
    """, (booking_id,))

    if not booking:
        abort(404)

    if booking['booking_status'] == 'Cancelled':
        flash("Payments cannot be recorded against a cancelled booking.", 'danger')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    paid_row = query_one("""
        SELECT COALESCE(SUM(amount), 0) AS total_paid
        FROM PAYMENT
        WHERE booking_id = %s AND payment_status = 'Completed'
    """, (booking_id,))
    total_paid = float(paid_row['total_paid']) if paid_row else 0.0
    balance_due = float(booking['total_amount']) - total_paid

    if balance_due <= 0:
        flash("This booking is already fully settled. No further payment is required.", 'info')
        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    if request.method == 'POST':
        amount_str = request.form.get('amount', '').strip()
        payment_method = request.form.get('payment_method', '').strip()
        payment_status = request.form.get('payment_status', 'Completed').strip()
        payment_date_str = request.form.get('payment_date', '').strip()

        errors = []

        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("Payment amount must be greater than zero.")
            elif amount > balance_due + 0.01:
                errors.append(
                    f"Payment ₹{amount:,.2f} exceeds the remaining balance "
                    f"₹{balance_due:,.2f}. Overpayment is not permitted."
                )
        except ValueError:
            errors.append("A valid numeric payment amount is required.")
            amount = 0.0

        if payment_method not in VALID_PAYMENT_METHODS:
            errors.append(f"Invalid payment method. Choose: {', '.join(VALID_PAYMENT_METHODS)}")

        if payment_status not in VALID_PAYMENT_STATUSES_FORM:
            errors.append("Invalid payment status selected.")

        try:
            payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date() \
                           if payment_date_str else date.today()
        except ValueError:
            errors.append("Invalid payment date. Use YYYY-MM-DD format.")
            payment_date = date.today()

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'payment_new.html',
                booking=booking, total_paid=total_paid, balance_due=balance_due,
                payment_methods=VALID_PAYMENT_METHODS,
                payment_statuses=VALID_PAYMENT_STATUSES_FORM,
                form_data=request.form
            )

        try:
            execute_commit("""
                INSERT INTO PAYMENT (booking_id, payment_date, amount, payment_method, payment_status)
                VALUES (%s, %s, %s, %s, %s)
            """, (booking_id, payment_date, amount, payment_method, payment_status))
            flash(
                f"Payment of ₹{amount:,.2f} via {payment_method} recorded "
                f"successfully for Booking #{booking_id}.",
                'success'
            )
        except Exception as e:
            logger.error("Payment insert failed for booking %s: %s", booking_id, e)
            flash("A database error occurred while recording the payment. Please try again.", 'danger')
            return render_template(
                'payment_new.html',
                booking=booking, total_paid=total_paid, balance_due=balance_due,
                payment_methods=VALID_PAYMENT_METHODS,
                payment_statuses=VALID_PAYMENT_STATUSES_FORM,
                form_data=request.form
            )

        return redirect(url_for('bookings.booking_detail', booking_id=booking_id))

    return render_template(
        'payment_new.html',
        booking=booking,
        total_paid=total_paid,
        balance_due=balance_due,
        payment_methods=VALID_PAYMENT_METHODS,
        payment_statuses=VALID_PAYMENT_STATUSES_FORM,
        form_data={}
    )
