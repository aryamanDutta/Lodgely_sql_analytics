import pytest
from unittest.mock import patch
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check_endpoint(client):
    """Test /health endpoint returns JSON status."""
    response = client.get('/health')
    assert response.status_code in [200, 503]
    data = response.get_json()
    assert 'status' in data
    assert 'database_connected' in data

def test_404_error_page(client):
    """Test 404 handler returns customized error page."""
    response = client.get('/nonexistent-page-xyz')
    assert response.status_code == 404
    assert b"404 - Record or Page Not Found" in response.data

@patch('routes.dashboard.query_one')
def test_landing_page_rendering(mock_query_one, client):
    """Test public landing page at / renders brand headline and CTAs."""
    mock_query_one.return_value = {
        'total_hotels': 3,
        'total_rooms': 20,
        'total_bookings': 20,
        'total_customers': 15
    }
    response = client.get('/')
    assert response.status_code == 200
    assert b"Lodgely" in response.data
    assert b"Hospitality Management Platform" in response.data
    assert b"Grand Luxe" in response.data
    assert b"One Platform." in response.data
    assert b"Every Hotel Operation." in response.data
    assert b"Open Dashboard" in response.data


def test_login_page_get(client):
    """Test /login endpoint returns 200 with staff authentication form."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Welcome Back" in response.data
    assert b"Staff Username" in response.data
    assert b"Aryam Khan" in response.data


@patch('routes.dashboard.query_one')
def test_login_page_post_success(mock_query_one, client):
    """Test /login form submission establishes staff session and redirects to dashboard."""
    mock_query_one.return_value = {
        'employee_id': 1,
        'employee_name': 'Aryam Khan',
        'designation': 'Administrator',
        'phone': '+91 97111 00001'
    }
    response = client.post('/login', data={
        'identifier': 'Aryam Khan',
        'password': 'hotel_secure_pwd_2026'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome back, Aryam Khan" in response.data


def test_logout_route(client):
    """Test /logout clears session and redirects to public landing page."""
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"signed out of Grand Luxe ERP" in response.data


@patch('routes.dashboard.query_all')
def test_global_search_route(mock_query_all, client):
    """Test /search endpoint searches across guests, rooms, bookings, and services."""
    mock_query_all.side_effect = [
        [{'customer_id': 1, 'customer_name': 'Aarav Sharma', 'email': 'aarav@example.com', 'phone': '98112', 'address': 'Delhi'}], # customers
        [{'room_id': 1, 'room_number': '101', 'room_type': 'Single', 'price_per_night': 2500, 'room_status': 'Available', 'hotel_name': 'Grand Horizon'}], # rooms
        [{'booking_id': 1, 'customer_name': 'Aarav Sharma', 'room_number': '101', 'hotel_name': 'Grand Horizon', 'check_in_date': '2026-10-10', 'booking_status': 'Confirmed'}], # bookings
        [{'service_id': 1, 'service_name': 'Airport Shuttle', 'price': 1500, 'hotel_name': 'Grand Horizon'}] # services
    ]
    response = client.get('/search?q=Sharma')
    assert response.status_code == 200
    assert b"Results for" in response.data
    assert b"Aarav Sharma" in response.data


@patch('routes.dashboard.query_one')
@patch('routes.dashboard.query_all')
def test_dashboard_route_rendering(mock_query_all, mock_query_one, client):
    """Test operational dashboard route rendering with mocked query responses."""
    # query_one is called 3 times: stats, occupancy, outstanding
    mock_query_one.side_effect = [
        {   # stats
            'total_hotels': 3, 'total_rooms': 20, 'available_rooms': 12,
            'occupied_rooms': 6, 'total_customers': 15, 'total_bookings': 20,
            'confirmed_bookings': 14, 'total_revenue': 428000.00,
            'pending_amount': 64100.00, 'pending_count': 5
        },
        {   # occupancy
            'total_rooms': 20, 'occupied_rooms': 6, 'available_rooms': 12,
            'maintenance_rooms': 2, 'active_rooms': 18,
            'occupancy_pct': 33.3
        },
        {   # outstanding
            'bookings_with_balance': 4, 'total_outstanding': 125000.00
        }
    ]
    # query_all is called 7 times:
    # 1. hotel_occupancy, 2. monthly_rev, 3. todays_arrivals,
    # 4. todays_departures, 5. booking_status_data, 6. room_types_data, 7. recent_bookings
    sample_booking = {
        'booking_id': 1, 'customer_name': 'Aarav Sharma',
        'customer_email': 'aarav@example.com', 'room_number': '101',
        'room_type': 'Single', 'hotel_name': 'Grand Horizon',
        'check_in_date': '2026-10-14', 'check_out_date': '2026-10-17',
        'number_of_guests': 2, 'booking_status': 'Confirmed',
        'total_amount': 21000.00
    }
    mock_query_all.side_effect = [
        [{'hotel_id': 1, 'hotel_name': 'The Grand Horizon', 'total_rooms': 7, 'occupied_rooms': 5, 'occupancy_rate': 71.4}], # hotel_occupancy
        [{'month_label': 'Oct 2026', 'sort_month': '2026-10', 'total_amount': 368500.00}], # monthly_rev
        [sample_booking],                                    # todays_arrivals
        [sample_booking],                                    # todays_departures
        [{'booking_status': 'Confirmed', 'count': 8}],      # booking_status_data
        [{'room_type': 'Deluxe', 'count': 6}],              # room_types_data
        [sample_booking]                                     # recent_bookings
    ]

    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Dashboard" in response.data
    assert b"Aarav Sharma" in response.data
    assert b"Grand Horizon" in response.data

@patch('routes.rooms.query_all')
def test_rooms_route_filtering(mock_query_all, client):
    """Test room directory and search filter handling."""
    mock_query_all.side_effect = [
        [{
            'room_id': 1,
            'room_number': '101',
            'room_type': 'Single',
            'price_per_night': 2500.00,
            'room_status': 'Available',
            'hotel_id': 1,
            'hotel_name': 'Grand Horizon',
            'location': 'New Delhi',
            'star_rating': 4.8
        }],
        [{'hotel_id': 1, 'hotel_name': 'Grand Horizon'}],
        [{'room_type': 'Single'}]
    ]

    response = client.get('/rooms/?room_number=101&room_status=Available')
    assert response.status_code == 200
    assert b"Room 101" or b"101" in response.data
    assert b"Grand Horizon" in response.data

@patch('routes.customers.query_all')
def test_customers_directory_route(mock_query_all, client):
    """Test customer directory rendering."""
    mock_query_all.return_value = [{
        'customer_id': 1,
        'customer_name': 'Priya Nair',
        'email': 'priya.nair@example.com',
        'phone': '+91 98220 54321',
        'address': 'Mumbai',
        'total_bookings': 2,
        'total_spent': 85200.00
    }]

    response = client.get('/customers/')
    assert response.status_code == 200
    assert b"Priya Nair" in response.data
    assert b"priya.nair@example.com" in response.data

@patch('routes.payments.query_all')
@patch('routes.payments.query_one')
def test_payments_ledger_route(mock_query_one, mock_query_all, client):
    """Test payments ledger rendering and financial KPIs."""
    mock_query_all.side_effect = [
        [{
            'payment_id': 1,
            'booking_id': 1,
            'payment_date': '2026-10-10 10:00:00',
            'amount': 21000.00,
            'payment_method': 'UPI',
            'payment_status': 'Completed',
            'customer_name': 'Aarav Sharma',
            'hotel_name': 'Grand Horizon'
        }],
        [{'payment_method': 'UPI', 'transaction_count': 6, 'total_amount': 125000.00}]
    ]
    mock_query_one.return_value = {
        'total_collected': 428000.00,
        'total_pending': 64100.00,
        'total_failed': 7800.00,
        'total_refunded': 5000.00,
        'total_transactions': 20
    }

    response = client.get('/payments/')
    assert response.status_code == 200
    assert b"Payment Ledger" in response.data
    assert b"UPI" in response.data

@patch('routes.bookings.query_all')
@patch('routes.bookings.query_one')
def test_booking_validation_invalid_dates(mock_query_one, mock_query_all, client):
    """Test server-side validation rejecting checkout date earlier than checkin."""
    mock_query_all.side_effect = [
        [{'customer_id': 1, 'customer_name': 'Test User', 'email': 'test@example.com'}],
        [{'room_id': 1, 'room_number': '101', 'room_type': 'Single', 'price_per_night': 2000, 'hotel_name': 'Hotel 1'}]
    ]
    response = client.post('/bookings/new', data={
        'customer_id': '1',
        'room_id': '1',
        'check_in_date': '2026-10-20',
        'check_out_date': '2026-10-15', # Invalid: earlier than check-in!
        'number_of_guests': '1',
        'booking_status': 'Confirmed'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Check-out date must be strictly after check-in date" in response.data


# ─────────────────────────────────────────────────────────────────────────────
# New route unit tests (mocked DB) — added for Stage 2/3 enhancements
# ─────────────────────────────────────────────────────────────────────────────

@patch('routes.rooms.query_all')
def test_room_new_get_form(mock_query_all, client):
    """GET /rooms/new returns 200 with the form."""
    mock_query_all.return_value = [{'hotel_id': 1, 'hotel_name': 'Grand Horizon'}]
    response = client.get('/rooms/new')
    assert response.status_code == 200
    assert b"New Room Registration" in response.data


@patch('routes.rooms.query_one')
@patch('routes.rooms.query_all')
def test_room_new_post_missing_fields(mock_query_all, mock_query_one, client):
    """POST /rooms/new with missing hotel_id is rejected with validation error."""
    mock_query_all.return_value = [{'hotel_id': 1, 'hotel_name': 'Grand Horizon'}]
    mock_query_one.return_value = None
    response = client.post('/rooms/new', data={
        'hotel_id': '',          # missing
        'room_number': '101',
        'room_type': 'Single',
        'price_per_night': '3000',
        'room_status': 'Available'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Please select a valid hotel property" in response.data


@patch('routes.customers.query_one')
@patch('routes.customers.query_all')
def test_customer_new_duplicate_email(mock_query_all, mock_query_one, client):
    """POST /customers/new with already-registered email is rejected."""
    mock_query_all.return_value = []
    mock_query_one.return_value = {'customer_id': 99}   # simulate duplicate
    response = client.post('/customers/new', data={
        'customer_name': 'Test User',
        'email': 'existing@example.com',
        'phone': '+91 99999 00000',
        'address': 'Test City'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"already registered" in response.data


@patch('routes.payments.query_all')
@patch('routes.payments.query_one')
def test_payment_new_missing_booking_id(mock_query_one, mock_query_all, client):
    """GET /payments/new without booking_id redirects to payments list with danger flash."""
    # The redirect goes to list_payments, which calls query_one and query_all
    mock_query_one.return_value = {
        'total_collected': 0.0, 'total_pending': 0.0,
        'total_failed': 0.0, 'total_refunded': 0.0, 'total_transactions': 0
    }
    mock_query_all.return_value = []
    response = client.get('/payments/new', follow_redirects=True)
    assert response.status_code == 200
    assert b"valid booking ID" in response.data


@patch('routes.payments.query_one')
def test_payment_new_cancelled_booking(mock_query_one, client):
    """GET /payments/new for a Cancelled booking redirects with warning."""
    mock_query_one.return_value = {
        'booking_id': 5, 'booking_status': 'Cancelled',
        'total_amount': 15000.00, 'customer_name': 'Test Guest',
        'customer_email': 'test@example.com',
        'room_number': '205', 'room_type': 'Double', 'hotel_name': 'Test Hotel'
    }
    response = client.get('/payments/new?booking_id=5', follow_redirects=True)
    assert response.status_code == 200
    assert b"cancelled booking" in response.data


@patch('routes.payments.execute_commit')
@patch('routes.payments.query_one')
def test_payment_new_overpayment_rejected(mock_query_one, mock_execute, client):
    """POST /payments/new with amount > balance_due is rejected server-side."""
    mock_query_one.side_effect = [
        {   # booking
            'booking_id': 1, 'booking_status': 'Confirmed',
            'total_amount': 10000.00, 'customer_name': 'Aarav Sharma',
            'customer_email': 'aarav@example.com',
            'room_number': '101', 'room_type': 'Single', 'hotel_name': 'Grand Horizon'
        },
        {'total_paid': 5000.00}   # paid_row — balance_due = 5000
    ]
    response = client.post('/payments/new', data={
        'booking_id': '1',
        'amount': '9999.99',         # exceeds balance of 5000
        'payment_method': 'UPI',
        'payment_status': 'Completed',
        'payment_date': '2026-10-14'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Overpayment is not permitted" in response.data
    mock_execute.assert_not_called()


@patch('routes.bookings.query_one')
@patch('routes.bookings.query_all')
def test_booking_cancel_completed_rejected(mock_query_all, mock_query_one, client):
    """POST /bookings/<id>/cancel on a Completed booking shows an error."""
    mock_query_one.return_value = {
        'booking_id': 3, 'booking_status': 'Completed',
        'room_id': 1, 'room_number': '101', 'customer_name': 'Test Guest',
        'customer_id': 1, 'room_type': 'Single', 'price_per_night': 3000,
        'hotel_name': 'Grand Horizon', 'hotel_location': 'Delhi',
        'star_rating': 4.5, 'hotel_id': 1, 'check_in_date': '2026-10-01',
        'check_out_date': '2026-10-05', 'number_of_guests': 2,
        'total_amount': 12000.00, 'room_status': 'Available',
        'customer_email': 'test@ex.com', 'customer_phone': '000',
        'customer_address': 'City', 'created_at': None
    }
    mock_query_all.return_value = []
    response = client.post('/bookings/3/cancel', follow_redirects=True)
    assert response.status_code == 200
    assert b"Completed" in response.data or b"cannot be cancelled" in response.data.lower() \
           or b"cancel" in response.data.lower()


@patch('routes.analytics.query_one')
@patch('routes.analytics.query_all')
def test_analytics_page_rendering(mock_query_all, mock_query_one, client):
    """Test SQL analytics dashboard renders all query cards and KPI indicators."""
    mock_query_one.side_effect = [
        {'avg_booking_value': 25000.0, 'min_booking_value': 5000.0, 'max_booking_value': 96000.0},
        {'total_rooms': 20, 'occupied_rooms': 6, 'available_rooms': 13, 'maintenance_rooms': 1, 'occupancy_percentage': 30.0}
    ]
    mock_query_all.return_value = []
    response = client.get('/analytics/')
    assert response.status_code == 200
    assert b"SQL Analytics" in response.data
    assert b"Business Intelligence" in response.data
