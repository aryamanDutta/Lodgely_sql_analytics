# SQL Query Documentation — Hotel Management System (CAM 5)

This document provides a comprehensive catalogue of the representative SQL queries implemented across the **Grand Luxe Hotel Management System**. Each query is executed directly against the MySQL 8.0 relational database (`hotel_management`) and demonstrates fundamental DBMS concepts including **Projection, Filtering, Sorting, Multi-table JOINs, Grouping, Aggregate Functions, and Subqueries**.

---

## Summary of DBMS Concepts Demonstrated

| Query # | Query Focus | DBMS Concepts Demonstrated | Page / Feature |
|---------|-------------|----------------------------|----------------|
| **Q1** | Real-Time Dashboard KPI Metrics | Subqueries, COUNT, SUM, Projection | Dashboard |
| **Q2** | Room Inventory with Hotel Details | Multi-table INNER JOIN, Parameterized Filtering, Sorting | Room Management |
| **Q3** | Recent Reservations Feed | 4-Table INNER JOIN, Date Filtering, Limit | Dashboard & Reservations |
| **Q4** | Reservation Overlap Verification | Subquery / Overlap Check, Concurrency Control | New Booking Form |
| **Q5** | Customer Spend & Booking Aggregation | LEFT JOIN, GROUP BY, SUM, COUNT, CASE Expression | Customer Directory |
| **Q6** | Payment Ledger & Channel Breakdown | INNER JOIN, Filtering, GROUP BY, SUM | Payments & Billing |
| **Q7** | Monthly Revenue Collection Trend | DATE_FORMAT, Aggregate SUM, GROUP BY, Sorting | Analytics (Query 7) |
| **Q8** | Room Occupancy & Utilization Rate | Mathematical Aggregation, CASE Expression, ROUND | Analytics (Query 11) |
| **Q9** | Top 5 Most Frequently Booked Rooms | 3-Table INNER JOIN, GROUP BY, SUM, ORDER BY DESC, LIMIT | Analytics (Query 8) |
| **Q10** | High-Value Guest Ranking | INNER JOIN, GROUP BY, HAVING / Aggregation, ORDER BY | Analytics (Query 9) |
| **Q11** | Room Rates & Inventory by Category | MIN, MAX, AVG, COUNT, GROUP BY | Analytics (Query 2) |
| **Q12** | Dining Menu & Outlet Inventory | 3-Table INNER JOIN, Multi-condition WHERE Filter | Restaurant & Dining |
| **Q13** | Sanitation & Housekeeping Audit | 4-Table INNER JOIN, Status & Date Filtering | Housekeeping Logs |
| **Q14** | Departmental Payroll & Role Diversity | COUNT, AVG, COUNT(DISTINCT) | Staff Directory |

---

## Detailed Query Specifications

### Query 1: Dashboard KPI Metrics (Aggregated Subqueries)
- **Purpose**: Retrieve global system totals in a single atomic database trip to populate top executive summary cards. Clearly separates actual collected revenue from pending invoices.
- **Tables Used**: `HOTEL`, `ROOM`, `CUSTOMER`, `BOOKING`, `PAYMENT`
- **Application Page**: `dashboard.py` &rarr; `dashboard.html`
- **SQL Statement**:
```sql
SELECT 
    (SELECT COUNT(*) FROM HOTEL) AS total_hotels,
    (SELECT COUNT(*) FROM ROOM) AS total_rooms,
    (SELECT COUNT(*) FROM ROOM WHERE room_status = 'Available') AS available_rooms,
    (SELECT COUNT(*) FROM CUSTOMER) AS total_customers,
    (SELECT COUNT(*) FROM BOOKING) AS total_bookings,
    (SELECT COUNT(*) FROM BOOKING WHERE booking_status = 'Confirmed') AS confirmed_bookings,
    (SELECT COALESCE(SUM(amount), 0) FROM PAYMENT WHERE payment_status = 'Completed') AS total_revenue,
    (SELECT COALESCE(SUM(amount), 0) FROM PAYMENT WHERE payment_status = 'Pending') AS pending_amount,
    (SELECT COUNT(*) FROM PAYMENT WHERE payment_status = 'Pending') AS pending_count;
```
- **Expected Result**: A single row containing 9 projected numerical columns.

---

### Query 2: Room Search and Inventory Filtering with Hotel Join
- **Purpose**: Allow front-desk staff to filter rooms by property, category, availability status, and price range, with controlled sorting.
- **Tables Used**: `ROOM r`, `HOTEL h`
- **Application Page**: `rooms.py` &rarr; `rooms.html`
- **SQL Statement**:
```sql
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
WHERE r.room_number LIKE %s
  AND r.hotel_id = %s
  AND r.room_type = %s
  AND r.room_status = %s
  AND r.price_per_night >= %s
  AND r.price_per_night <= %s
ORDER BY r.price_per_night ASC;
```
- **Expected Result**: Tabular dataset showing room details accompanied by the associated hotel name and location.

---

### Query 3: Multi-Table Joined Reservation Log
- **Purpose**: Display recent reservations including customer contact info, assigned room details, and hotel branch name.
- **Tables Used**: `BOOKING b`, `CUSTOMER c`, `ROOM r`, `HOTEL h`
- **Application Page**: `dashboard.py` & `bookings.py`
- **SQL Statement**:
```sql
SELECT 
    b.booking_id,
    b.customer_id,
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
LIMIT 6;
```
- **Expected Result**: List of recent reservations ordered chronologically by newest reservation ID.

---

### Query 4: Double-Booking Overlap Prevention Check
- **Purpose**: Verify if a room already has an active overlapping reservation prior to confirming a new booking.
- **Tables Used**: `BOOKING`
- **Application Page**: `bookings.py` (`new_booking()` route)
- **SQL Statement**:
```sql
SELECT COUNT(*) AS overlap_count
FROM BOOKING
WHERE room_id = %s
  AND booking_status IN ('Confirmed', 'Completed')
  AND check_in_date < %s
  AND check_out_date > %s;
```
- **Expected Result**: Count of conflicting bookings. If count > 0, reservation insertion is rejected with a validation error.

---

### Query 5: Customer Directory with Aggregated Lifetime Value
- **Purpose**: Calculate total number of bookings and cumulative spending for each customer profile, including customers who have not yet made a booking (via LEFT JOIN).
- **Tables Used**: `CUSTOMER c`, `BOOKING b`
- **Application Page**: `customers.py` &rarr; `customers.html`
- **SQL Statement**:
```sql
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
WHERE c.customer_name LIKE %s
GROUP BY c.customer_id, c.customer_name, c.email, c.phone, c.address
ORDER BY c.customer_name ASC;
```
- **Expected Result**: List of customers with aggregated metrics, preserving zero values for inactive users.

---

### Query 6: Payment Channel Breakdown
- **Purpose**: Group all financial payments by payment method to evaluate payment gateway usage and settlement totals.
- **Tables Used**: `PAYMENT`
- **Application Page**: `payments.py` &rarr; `payments.html`
- **SQL Statement**:
```sql
SELECT 
    payment_method,
    COUNT(*) AS transaction_count,
    COALESCE(SUM(amount), 0) AS total_amount,
    COALESCE(AVG(amount), 0) AS avg_amount
FROM PAYMENT
GROUP BY payment_method
ORDER BY total_amount DESC;
```
- **Expected Result**: Table with channels ('UPI', 'Credit Card', 'Net Banking', etc.), count, total volume, and average transaction size.

---

### Query 7: Monthly Collected Revenue Trend (Completed Payments Only)
- **Purpose**: Group verified payments by calendar month to analyze historical financial growth.
- **Tables Used**: `PAYMENT`
- **Application Page**: `analytics.py` &rarr; `analytics.html`
- **SQL Statement**:
```sql
SELECT 
    DATE_FORMAT(payment_date, '%Y-%m') AS payment_month,
    COUNT(*) AS completed_transactions,
    COALESCE(SUM(amount), 0) AS total_revenue_collected
FROM PAYMENT
WHERE payment_status = 'Completed'
GROUP BY DATE_FORMAT(payment_date, '%Y-%m')
ORDER BY payment_month ASC;
```
- **Expected Result**: Chronological monthly series of realized revenue feed into the Chart.js line graph.

---

### Query 8: Room Occupancy Rate & Utilization Metric
- **Purpose**: Calculate the exact current room occupancy percentage across the hotel chain.
- **Tables Used**: `ROOM`
- **Application Page**: `analytics.py` &rarr; `analytics.html`
- **Formula**: `(Occupied Rooms / Total Rooms) * 100`
- **SQL Statement**:
```sql
SELECT 
    COUNT(*) AS total_rooms,
    SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
    SUM(CASE WHEN room_status = 'Available' THEN 1 ELSE 0 END) AS available_rooms,
    SUM(CASE WHEN room_status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_rooms,
    ROUND((SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS occupancy_percentage
FROM ROOM;
```
- **Expected Result**: Single row with exact breakdown counts and calculated utilization percentage.

---

### Query 9: Top 5 Most Popular Rooms by Booking Frequency
- **Purpose**: Identify the hotel's top-performing rooms by reservation frequency and revenue generation.
- **Tables Used**: `BOOKING b`, `ROOM r`, `HOTEL h`
- **Application Page**: `analytics.py` &rarr; `analytics.html`
- **SQL Statement**:
```sql
SELECT 
    r.room_number,
    r.room_type,
    h.hotel_name, 
    COUNT(b.booking_id) AS total_bookings,
    COALESCE(SUM(b.total_amount), 0) AS total_revenue_generated
FROM BOOKING b
INNER JOIN ROOM r ON b.room_id = r.room_id
INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
GROUP BY r.room_id, r.room_number, r.room_type, h.hotel_name
ORDER BY total_bookings DESC, total_revenue_generated DESC
LIMIT 5;
```
- **Expected Result**: Top 5 rooms ranked by highest booking count and generated revenue.

---

### Query 10: High-Value VIP Guests
- **Purpose**: Extract customer profiles with the highest number of stays and total billing volume.
- **Tables Used**: `CUSTOMER c`, `BOOKING b`
- **Application Page**: `analytics.py` &rarr; `analytics.html`
- **SQL Statement**:
```sql
SELECT 
    c.customer_name,
    c.email,
    c.phone,
    COUNT(b.booking_id) AS bookings_count,
    COALESCE(SUM(b.total_amount), 0) AS total_spent
FROM CUSTOMER c
INNER JOIN BOOKING b ON c.customer_id = b.customer_id
GROUP BY c.customer_id, c.customer_name, c.email, c.phone
ORDER BY bookings_count DESC, total_spent DESC
LIMIT 5;
```
- **Expected Result**: Top 5 loyal guests with their total spend and reservations count.

---

### Query 11: Room Pricing Distribution by Category
- **Purpose**: Aggregate inventory count and evaluate price boundaries (MIN, MAX, AVG) per room category.
- **Tables Used**: `ROOM`
- **Application Page**: `analytics.py` &rarr; `analytics.html`
- **SQL Statement**:
```sql
SELECT 
    room_type,
    COUNT(*) AS room_count, 
    MIN(price_per_night) AS min_price, 
    MAX(price_per_night) AS max_price, 
    AVG(price_per_night) AS avg_price
FROM ROOM
GROUP BY room_type
ORDER BY room_count DESC;
```
- **Expected Result**: Room category breakdown with min, max, and computed average tariffs.

---

### Query 12: Restaurant Menu Items Joined with Outlets and Hotels
- **Purpose**: Provide full cross-facility dining menu listing with outlet opening hours and cuisine types.
- **Tables Used**: `FOOD f`, `RESTAURANT r`, `HOTEL h`
- **Application Page**: `restaurants.py` &rarr; `restaurants.html`
- **SQL Statement**:
```sql
SELECT 
    f.food_id,
    f.food_name,
    f.category,
    f.price,
    f.availability,
    r.restaurant_id,
    r.restaurant_name,
    r.cuisine_type,
    r.opening_hours,
    h.hotel_name
FROM FOOD f
INNER JOIN RESTAURANT r ON f.restaurant_id = r.restaurant_id
INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
WHERE f.availability = 'Available'
  AND f.price <= 500.00
ORDER BY r.restaurant_name, f.food_name ASC;
```
- **Expected Result**: Multi-table joined catalog of available dining options matching dietary and price filters.

---

### Query 13: Housekeeping Logs with Staff and Room Attributes
- **Purpose**: Audit hotel sanitation status by linking housekeeping logs with assigned staff and room numbers.
- **Tables Used**: `HOUSEKEEPING hk`, `ROOM r`, `HOTEL h`, `EMPLOYEE e`
- **Application Page**: `housekeeping.py` &rarr; `housekeeping.html`
- **SQL Statement**:
```sql
SELECT 
    hk.housekeeping_id,
    hk.cleaning_date,
    hk.cleaning_status,
    r.room_id,
    r.room_number,
    r.room_type,
    r.room_status,
    e.employee_id,
    e.employee_name,
    h.hotel_name
FROM HOUSEKEEPING hk
INNER JOIN ROOM r ON hk.room_id = r.room_id
INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
INNER JOIN EMPLOYEE e ON hk.employee_id = e.employee_id
WHERE hk.cleaning_status = 'Pending Inspection'
ORDER BY hk.cleaning_date DESC;
```
- **Expected Result**: Operational log of rooms pending inspection before front-desk release.

---

### Query 14: Departmental Staffing and Payroll Summary
- **Purpose**: Audit workforce metrics across the properties.
- **Tables Used**: `EMPLOYEE`
- **Application Page**: `employees.py` &rarr; `employees.html`
- **SQL Statement**:
```sql
SELECT 
    COUNT(*) AS total_employees,
    COALESCE(AVG(salary), 0) AS avg_salary,
    COUNT(DISTINCT designation) AS total_roles
FROM EMPLOYEE;
```
- **Expected Result**: Workforce aggregates showing total headcount, average compensation, and distinct organizational designations.


---

### Query 15: Date-Range Room Availability Search (Subquery Anti-Join)
- **Purpose**: Search for rooms strictly available during a guest's desired stay dates, excluding any rooms with overlapping active reservations or maintenance tags.
- **Tables Used**: `ROOM r`, `HOTEL h`, `BOOKING b`
- **Application Page**: `rooms.py` &rarr; `rooms.html`
- **SQL Statement**:
```sql
SELECT 
    r.room_id,
    r.room_number,
    r.room_type,
    r.price_per_night,
    r.room_status,
    h.hotel_name,
    h.location
FROM ROOM r
INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
WHERE r.room_status != 'Maintenance'
  AND r.room_id NOT IN (
      SELECT b.room_id 
      FROM BOOKING b 
      WHERE b.booking_status IN ('Confirmed', 'Completed')
        AND b.check_in_date < %s   /* desired check-out date */
        AND b.check_out_date > %s  /* desired check-in date */
  )
ORDER BY r.price_per_night ASC;
```
- **DBMS Concept**: Subquery filtering (`NOT IN`), interval overlap logic (`check_in < req_out AND check_out > req_in`), parameterized safety.

---

### Query 16: Live Operational Occupancy Rate (Active Capacity Metrics)
- **Purpose**: Compute true live property utilization by calculating occupied rooms against active rentable rooms (excluding inventory out-of-order for maintenance).
- **Tables Used**: `ROOM`
- **Application Page**: `dashboard.py` &rarr; `dashboard.html`
- **SQL Statement**:
```sql
SELECT
    COUNT(*) AS total_rooms,
    SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
    SUM(CASE WHEN room_status != 'Maintenance' THEN 1 ELSE 0 END) AS active_rooms,
    ROUND(
        SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN room_status != 'Maintenance' THEN 1 ELSE 0 END), 0) * 100
    , 1) AS occupancy_pct
FROM ROOM;
```
- **DBMS Concept**: Conditional aggregation (`SUM(CASE ...)`), `NULLIF` divide-by-zero prevention, floating point rounding.

---

### Query 17: Outstanding Reservation Balances (Financial Receivables Audit)
- **Purpose**: Identify unpaid or partially paid guest reservations with outstanding balances to protect hotel revenue.
- **Tables Used**: `BOOKING b`, `CUSTOMER c`, `ROOM r`, `HOTEL h`, `PAYMENT`
- **Application Page**: `analytics.py` &rarr; `analytics.html` (Query 13)
- **SQL Statement**:
```sql
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
ORDER BY balance_due DESC;
```
- **DBMS Concept**: Derived table / subquery join with `GROUP BY`, multi-table `INNER JOIN`, arithmetic expression in projection and `WHERE` filter.

---

### Query 18: Housekeeping Workload Distribution & Cleaning Audit
- **Purpose**: Measure staff efficiency and department workload by aggregating clean, dirty, and in-progress room tasks per housekeeper.
- **Tables Used**: `EMPLOYEE e`, `HOTEL h`, `HOUSEKEEPING hk`
- **Application Page**: `analytics.py` &rarr; `analytics.html` (Query 14)
- **SQL Statement**:
```sql
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
ORDER BY total_assignments DESC;
```
- **DBMS Concept**: `LEFT JOIN` preserving staff with 0 tasks, conditional counting with `SUM(CASE ...)`, multi-column `GROUP BY`.

---

### Query 19: Pessimistic Row Locking for Overlap-Free Reservation Writes
- **Purpose**: Prevent race conditions and double bookings under concurrent web requests by locking conflicting candidate rows within a single InnoDB transaction.
- **Tables Used**: `BOOKING`
- **Application Page**: `bookings.py` (`transaction_context()` block)
- **SQL Statement**:
```sql
SELECT booking_id 
FROM BOOKING 
WHERE room_id = %s 
  AND booking_status IN ('Confirmed', 'Completed')
  AND check_in_date < %s 
  AND check_out_date > %s
FOR UPDATE;
```
- **DBMS Concept**: InnoDB row-level locking (`FOR UPDATE`), ACID transaction isolation, pessimistic concurrency control.
