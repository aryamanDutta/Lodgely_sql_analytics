"""
Integration Test Suite for Hotel Management ERP.
Executes against live MySQL database (e.g., inside Docker container).
Skips gracefully if live MySQL is offline.
Cleans up all created test entities after each test to protect seed data.
"""

import pytest
from datetime import date, timedelta
from app import create_app
from db.connection import check_db_connection, query_one, query_all, execute_commit

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'integration-secret-key'
    return app

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()

@pytest.fixture(autouse=True)
def skip_if_no_db():
    if not check_db_connection():
        pytest.skip("Live MySQL database is not connected. Skipping integration tests.")

@pytest.fixture
def test_customer():
    """Create a temporary guest profile and ensure cleanup."""
    test_email = "integ_guest_auto@example.com"
    # Clean up any leftover from previous aborted runs
    execute_commit("DELETE FROM CUSTOMER WHERE email = %s", (test_email,))
    
    execute_commit("""
        INSERT INTO CUSTOMER (customer_name, email, phone, address)
        VALUES ('Integration Test Guest', %s, '+91 99999 11111', 'Integration Lab, City')
    """, (test_email,))
    
    cust = query_one("SELECT customer_id FROM CUSTOMER WHERE email = %s", (test_email,))
    cust_id = cust['customer_id']
    
    yield cust_id
    
    # Cleanup: remove any bookings first, then customer
    execute_commit("""
        DELETE FROM PAYMENT WHERE booking_id IN (
            SELECT booking_id FROM BOOKING WHERE customer_id = %s
        )
    """, (cust_id,))
    execute_commit("DELETE FROM BOOKING WHERE customer_id = %s", (cust_id,))
    execute_commit("DELETE FROM CUSTOMER WHERE customer_id = %s", (cust_id,))

@pytest.fixture
def test_room():
    """Create a temporary room in Hotel 1 and ensure cleanup."""
    test_room_no = "INT-901"
    execute_commit("DELETE FROM ROOM WHERE hotel_id = 1 AND room_number = %s", (test_room_no,))
    
    execute_commit("""
        INSERT INTO ROOM (hotel_id, room_number, room_type, price_per_night, room_status)
        VALUES (1, %s, 'Deluxe', 5000.00, 'Available')
    """, (test_room_no,))
    
    rm = query_one("SELECT room_id FROM ROOM WHERE hotel_id = 1 AND room_number = %s", (test_room_no,))
    room_id = rm['room_id']
    
    yield room_id
    
    # Cleanup
    execute_commit("""
        DELETE FROM PAYMENT WHERE booking_id IN (
            SELECT booking_id FROM BOOKING WHERE room_id = %s
        )
    """, (room_id,))
    execute_commit("DELETE FROM HOUSEKEEPING WHERE room_id = %s", (room_id,))
    execute_commit("DELETE FROM BOOKING WHERE room_id = %s", (room_id,))
    execute_commit("DELETE FROM ROOM WHERE room_id = %s", (room_id,))


def test_booking_creation_and_overlap_prevention(client, test_customer, test_room):
    """
    Test 1: Create a reservation with date validation.
    Attempting a conflicting booking for the same room must be rejected with overlap detection.
    """
    check_in = (date.today() + timedelta(days=30)).strftime('%Y-%m-%d')
    check_out = (date.today() + timedelta(days=34)).strftime('%Y-%m-%d')
    
    # First booking: should succeed
    res1 = client.post('/bookings/new', data={
        'customer_id': str(test_customer),
        'room_id': str(test_room),
        'check_in_date': check_in,
        'check_out_date': check_out,
        'number_of_guests': '2',
        'booking_status': 'Confirmed'
    }, follow_redirects=True)
    
    assert res1.status_code == 200
    assert b"successfully booked" in res1.data.lower() or b"confirmed" in res1.data.lower()
    
    # Second booking overlapping by 2 days: MUST be rejected
    overlap_in = (date.today() + timedelta(days=32)).strftime('%Y-%m-%d')
    overlap_out = (date.today() + timedelta(days=36)).strftime('%Y-%m-%d')
    
    res2 = client.post('/bookings/new', data={
        'customer_id': str(test_customer),
        'room_id': str(test_room),
        'check_in_date': overlap_in,
        'check_out_date': overlap_out,
        'number_of_guests': '1',
        'booking_status': 'Confirmed'
    }, follow_redirects=True)
    
    assert res2.status_code == 200
    assert b"already reserved" in res2.data.lower() or b"overlap" in res2.data.lower() or b"conflict" in res2.data.lower()


def test_booking_lifecycle_checkin_checkout(client, test_customer, test_room):
    """
    Test 2: Full reservation lifecycle:
    Confirmed -> Check In (room becomes Occupied) -> Check Out (room becomes Available + Housekeeping Dirty task created)
    """
    check_in = date.today().strftime('%Y-%m-%d')
    check_out = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    client.post('/bookings/new', data={
        'customer_id': str(test_customer),
        'room_id': str(test_room),
        'check_in_date': check_in,
        'check_out_date': check_out,
        'number_of_guests': '2',
        'booking_status': 'Confirmed'
    }, follow_redirects=True)
    
    booking = query_one("""
        SELECT booking_id FROM BOOKING 
        WHERE customer_id = %s AND room_id = %s 
        ORDER BY booking_id DESC LIMIT 1
    """, (test_customer, test_room))
    booking_id = booking['booking_id']
    
    # Check In
    cin_res = client.post(f'/bookings/{booking_id}/check-in', follow_redirects=True)
    assert cin_res.status_code == 200
    
    # Verify room status in MySQL is 'Occupied'
    room_status = query_one("SELECT room_status FROM ROOM WHERE room_id = %s", (test_room,))['room_status']
    assert room_status == 'Occupied'
    
    # Check Out
    cout_res = client.post(f'/bookings/{booking_id}/check-out', follow_redirects=True)
    assert cout_res.status_code == 200
    
    # Verify room status in MySQL reverted to 'Available'
    room_status_after = query_one("SELECT room_status FROM ROOM WHERE room_id = %s", (test_room,))['room_status']
    assert room_status_after == 'Available'
    
    # Verify booking status became 'Completed'
    b_status = query_one("SELECT booking_status FROM BOOKING WHERE booking_id = %s", (booking_id,))['booking_status']
    assert b_status == 'Completed'
    
    # Verify Housekeeping record was created
    hk = query_one("SELECT cleaning_status FROM HOUSEKEEPING WHERE room_id = %s ORDER BY housekeeping_id DESC LIMIT 1", (test_room,))
    assert hk is not None
    assert hk['cleaning_status'] == 'Dirty'


def test_payment_recording_and_overpayment_prevention(client, test_customer, test_room):
    """
    Test 3: Record payment in MySQL and verify that overpayment is rejected.
    """
    check_in = (date.today() + timedelta(days=40)).strftime('%Y-%m-%d')
    check_out = (date.today() + timedelta(days=42)).strftime('%Y-%m-%d')
    
    # 2 nights * 5000 = 10,000 total
    client.post('/bookings/new', data={
        'customer_id': str(test_customer),
        'room_id': str(test_room),
        'check_in_date': check_in,
        'check_out_date': check_out,
        'number_of_guests': '1',
        'booking_status': 'Confirmed'
    }, follow_redirects=True)
    
    booking = query_one("""
        SELECT booking_id, total_amount FROM BOOKING 
        WHERE customer_id = %s AND room_id = %s 
        ORDER BY booking_id DESC LIMIT 1
    """, (test_customer, test_room))
    booking_id = booking['booking_id']
    total_amt = float(booking['total_amount'])
    
    # Attempt overpayment: total + 1000
    bad_res = client.post('/payments/new', data={
        'booking_id': str(booking_id),
        'amount': str(total_amt + 1000.00),
        'payment_method': 'UPI',
        'payment_status': 'Completed',
        'payment_date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert b"exceeds the remaining balance" in bad_res.data.lower() or b"overpayment" in bad_res.data.lower()
    
    # Valid partial payment: 4,000
    good_res = client.post('/payments/new', data={
        'booking_id': str(booking_id),
        'amount': '4000.00',
        'payment_method': 'UPI',
        'payment_status': 'Completed',
        'payment_date': date.today().strftime('%Y-%m-%d')
    }, follow_redirects=True)
    assert good_res.status_code == 200
    assert b"recorded" in good_res.data.lower()
    
    # Check paid total in MySQL
    paid_sum = query_one("SELECT SUM(amount) AS s FROM PAYMENT WHERE booking_id = %s AND payment_status = 'Completed'", (booking_id,))['s']
    assert float(paid_sum) == 4000.00


def test_customer_referential_deletion_protection(client, test_customer, test_room):
    """
    Test 4: Attempting to delete a customer who has existing booking records
    must be blocked by server-side referential integrity check.
    """
    check_in = (date.today() + timedelta(days=50)).strftime('%Y-%m-%d')
    check_out = (date.today() + timedelta(days=52)).strftime('%Y-%m-%d')
    
    client.post('/bookings/new', data={
        'customer_id': str(test_customer),
        'room_id': str(test_room),
        'check_in_date': check_in,
        'check_out_date': check_out,
        'number_of_guests': '1',
        'booking_status': 'Confirmed'
    }, follow_redirects=True)
    
    # Attempt delete customer
    del_res = client.post(f'/customers/{test_customer}/delete', follow_redirects=True)
    assert del_res.status_code == 200
    assert b"cannot delete" in del_res.data.lower() or b"reservation record" in del_res.data.lower()
    
    # Verify customer still exists in MySQL
    cust = query_one("SELECT customer_id FROM CUSTOMER WHERE customer_id = %s", (test_customer,))
    assert cust is not None
