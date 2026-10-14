# CAM 5 Academic Laboratory Project Report
# Database-Driven Hotel Management ERP Web Application

---

**Course**: Database Management Systems Laboratory (CAM 5)  
**Academic Degree**: Bachelor of Technology in Computer Science & Engineering  
**Project Title**: Grand Luxe Hotel Management Database Web Application  
**Database**: MySQL 8.0  
**Backend**: Python 3.11 / Flask  
**Frontend**: HTML5, CSS3, Jinja2, Chart.js  
**Deployment**: Docker & Docker Compose  
**Date of Submission**: October 2026  

---

## 1. Problem Statement

Modern hospitality enterprises operate multi-property networks requiring simultaneous coordination across room inventory, customer reservations, payment settlements, culinary dining menus, guest amenities, human resources, and housekeeping operations.

Traditional spreadsheet-based or manual logbook systems suffer from critical limitations:
1. **Data Redundancy & Inconsistency**: Duplicate entries across room records and customer logbooks lead to data corruption.
2. **Double-Booking Errors**: Lack of concurrency control and atomic validation creates conflicting reservations for the same room.
3. **Financial Inaccuracy**: Ambiguity in tracking invoiced amounts versus actual cleared funds causes distorted financial reporting.
4. **Inefficient Operational Coordination**: Front-desk staff cannot readily access housekeeping readiness statuses, leading to delayed guest check-ins.
5. **Absence of Real-Time Business Intelligence**: Key operational metrics, such as room occupancy rates and revenue collection trends, cannot be evaluated on demand.

To resolve these challenges, this project implements a centralized, relational database management system (RDBMS) paired with an intuitive web application that enforces referential integrity, automated concurrency safeguards, and comprehensive analytical reporting.

---

## 2. Project Objectives

1. **Relational Database Design**: Architect a normalized MySQL 8.0 database (`hotel_management`) in Third Normal Form (3NF) spanning 10 core entities.
2. **Integrity Constraint Enforcement**: Implement primary keys, foreign keys with appropriate cascade rules, `UNIQUE` constraints, `NOT NULL` rules, and SQL `CHECK` constraints to restrict invalid data at the storage layer.
3. **Automated Concurrency & Overlap Prevention**: Enforce server-side transactional validation to eliminate overlapping confirmed bookings for any room.
4. **Selective Data Extraction & Parameterized Search**: Develop multi-criteria filtering interfaces using parameterized SQL queries to protect against SQL Injection vulnerabilities.
5. **Comprehensive DBMS Query Demonstration**: Implement and document complex queries demonstrating projection, multi-table `INNER JOIN` and `LEFT JOIN`, sorting, grouping (`GROUP BY`), and aggregation functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
6. **Executive Dashboard & Business Intelligence**: Deliver an administrative dashboard with real-time KPI summary cards, interactive charts, and 12 specialized analytical reports.
7. **Production Containerization**: Orchestrate the database and web tiers using Docker and Docker Compose with health checks and persistent volume storage.

---

## 3. Hardware & Software Requirements

### Hardware Requirements
- **Processor**: Intel Core i5 / AMD Ryzen 5 or higher (minimum 2.0 GHz multi-core).
- **RAM**: Minimum 8 GB (16 GB recommended for concurrent Docker containerization).
- **Storage**: Minimum 10 GB available SSD storage.
- **Display**: Standard 1080p display (1920x1080) for responsive dashboard viewing.

### Software Requirements
- **Operating System**: Windows 10/11 (64-bit), macOS, or Ubuntu Linux 22.04 LTS.
- **Database Server**: MySQL Server 8.0+.
- **Backend Runtime**: Python 3.11+ / Python 3.14.
- **Web Framework**: Flask 3.1+.
- **Database Driver**: PyMySQL 1.1+ with DictCursor.
- **Container Engine**: Docker Desktop 29+ with Docker Compose v2+.
- **Web Browser**: Google Chrome, Mozilla Firefox, or Microsoft Edge (Chromium).

---

## 4. Technology Stack Justification

- **MySQL 8.0**: Selected for ACID compliance, native support for SQL `CHECK` constraints, strong indexing capabilities (B-Tree), and enterprise adoption.
- **Python Flask**: A lightweight WSGI web application framework that provides complete architectural control without imposing rigid ORM abstractions, enabling direct execution of parameterized SQL statements.
- **PyMySQL**: A pure-Python MySQL client driver eliminating native binary compilation dependencies, simplifying container deployment and cross-platform execution.
- **Jinja2**: Server-side templating engine that dynamically compiles HTML using data extracted directly from MySQL queries without hardcoding.
- **HTML5 & Vanilla CSS3**: Engineered from scratch to produce a modern, responsive corporate dashboard theme with accessible semantic components and status indicators.
- **Chart.js**: Client-side canvas charting library used strictly where it adds business value (occupancy distribution and revenue trends), equipped with graceful fallback handling.
- **Docker Compose**: Ensures repeatable, isolated deployment of both the Flask web server and MySQL database with persistent named volumes.

---

## 5. System Architecture

The application adopts a three-tier architectural model:

```
+-------------------------------------------------------------+
|                     PRESENTATION TIER                       |
|  - HTML5 / CSS3 Responsive Dashboard & Navigation           |
|  - Dynamic Jinja2 Templates                                  |
|  - Interactive Visualizations (Chart.js)                    |
+-------------------------------------------------------------+
                              |
                              | HTTP / RESTful Requests (Port 5000)
                              v
+-------------------------------------------------------------+
|                      APPLICATION TIER                       |
|  - Flask Application Factory (`app.py`)                     |
|  - Modular Blueprints: Rooms, Bookings, Customers, Payments |
|  - Input Validation & Concurrency Overlap Verification      |
|  - Parameterized Query Builder & Transaction Control        |
+-------------------------------------------------------------+
                              |
                              | TCP / IP Connection Pool (Port 3306)
                              v
+-------------------------------------------------------------+
|                        DATABASE TIER                        |
|  - MySQL 8.0 Community Server (Containerized)               |
|  - InnoDB Storage Engine (ACID Compliant)                   |
|  - 10 Relational Entities (3NF Normalized)                  |
|  - B-Tree Composite Indexes & Referential Integrity         |
|  - Persistent Named Volume (`hotel_cam5_mysql_data`)        |
+-------------------------------------------------------------+
```

---

## 6. Database Schema & Relational Specifications

The schema is defined in `database/init.sql` and includes the following 10 relational entities:

### 1. `HOTEL`
- `hotel_id` INT AUTO_INCREMENT PRIMARY KEY
- `hotel_name` VARCHAR(100) NOT NULL
- `location` VARCHAR(200) NOT NULL
- `contact_number` VARCHAR(20) NOT NULL
- `star_rating` DECIMAL(2,1) NOT NULL CHECK (star_rating BETWEEN 1.0 AND 5.0)

### 2. `ROOM`
- `room_id` INT AUTO_INCREMENT PRIMARY KEY
- `hotel_id` INT NOT NULL (FK &rarr; `HOTEL.hotel_id` ON DELETE CASCADE)
- `room_number` VARCHAR(10) NOT NULL
- `room_type` VARCHAR(50) NOT NULL CHECK (room_type IN ('Single', 'Double', 'Deluxe', 'Suite', 'Presidential Suite'))
- `price_per_night` DECIMAL(10,2) NOT NULL CHECK (price_per_night > 0)
- `room_status` VARCHAR(20) NOT NULL DEFAULT 'Available' CHECK (room_status IN ('Available', 'Occupied', 'Maintenance'))
- UNIQUE (hotel_id, room_number)

### 3. `CUSTOMER`
- `customer_id` INT AUTO_INCREMENT PRIMARY KEY
- `customer_name` VARCHAR(100) NOT NULL
- `email` VARCHAR(100) NOT NULL UNIQUE
- `phone` VARCHAR(20) NOT NULL
- `address` VARCHAR(255) NOT NULL

### 4. `EMPLOYEE`
- `employee_id` INT AUTO_INCREMENT PRIMARY KEY
- `hotel_id` INT NOT NULL (FK &rarr; `HOTEL.hotel_id` ON DELETE CASCADE)
- `employee_name` VARCHAR(100) NOT NULL
- `designation` VARCHAR(50) NOT NULL
- `salary` DECIMAL(10,2) NOT NULL CHECK (salary > 0)
- `phone` VARCHAR(20) NOT NULL

### 5. `BOOKING`
- `booking_id` INT AUTO_INCREMENT PRIMARY KEY
- `customer_id` INT NOT NULL (FK &rarr; `CUSTOMER.customer_id` ON DELETE RESTRICT)
- `room_id` INT NOT NULL (FK &rarr; `ROOM.room_id` ON DELETE RESTRICT)
- `check_in_date` DATE NOT NULL
- `check_out_date` DATE NOT NULL
- `number_of_guests` INT NOT NULL DEFAULT 1 CHECK (number_of_guests > 0)
- `booking_status` VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (booking_status IN ('Confirmed', 'Pending', 'Cancelled', 'Completed'))
- `total_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (total_amount >= 0)
- CHECK (check_out_date >= check_in_date)

### 6. `PAYMENT`
- `payment_id` INT AUTO_INCREMENT PRIMARY KEY
- `booking_id` INT NOT NULL (FK &rarr; `BOOKING.booking_id` ON DELETE CASCADE)
- `payment_date` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
- `amount` DECIMAL(10,2) NOT NULL CHECK (amount > 0)
- `payment_method` VARCHAR(50) NOT NULL CHECK (payment_method IN ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash'))
- `payment_status` VARCHAR(20) NOT NULL DEFAULT 'Pending' CHECK (payment_status IN ('Completed', 'Pending', 'Failed', 'Refunded'))

### 7. `RESTAURANT`
- `restaurant_id` INT AUTO_INCREMENT PRIMARY KEY
- `hotel_id` INT NOT NULL (FK &rarr; `HOTEL.hotel_id` ON DELETE CASCADE)
- `restaurant_name` VARCHAR(100) NOT NULL
- `cuisine_type` VARCHAR(50) NOT NULL
- `opening_hours` VARCHAR(100) NOT NULL

### 8. `FOOD`
- `food_id` INT AUTO_INCREMENT PRIMARY KEY
- `restaurant_id` INT NOT NULL (FK &rarr; `RESTAURANT.restaurant_id` ON DELETE CASCADE)
- `food_name` VARCHAR(100) NOT NULL
- `category` VARCHAR(50) NOT NULL CHECK (category IN ('Appetizer', 'Main Course', 'Dessert', 'Beverage', 'Snacks'))
- `price` DECIMAL(10,2) NOT NULL CHECK (price > 0)
- `availability` VARCHAR(20) NOT NULL DEFAULT 'Available' CHECK (availability IN ('Available', 'Out of Stock'))

### 9. `SERVICE`
- `service_id` INT AUTO_INCREMENT PRIMARY KEY
- `hotel_id` INT NOT NULL (FK &rarr; `HOTEL.hotel_id` ON DELETE CASCADE)
- `service_name` VARCHAR(100) NOT NULL
- `description` TEXT
- `price` DECIMAL(10,2) NOT NULL DEFAULT 0.00 CHECK (price >= 0)

### 10. `HOUSEKEEPING`
- `housekeeping_id` INT AUTO_INCREMENT PRIMARY KEY
- `employee_id` INT NOT NULL (FK &rarr; `EMPLOYEE.employee_id` ON DELETE CASCADE)
- `room_id` INT NOT NULL (FK &rarr; `ROOM.room_id` ON DELETE CASCADE)
- `cleaning_date` DATE NOT NULL
- `cleaning_status` VARCHAR(30) NOT NULL DEFAULT 'Pending Inspection' CHECK (cleaning_status IN ('Clean', 'In Progress', 'Pending Inspection', 'Dirty'))

---

## 7. Sample Records Summary

The database is initialized with 114 deterministic records:
- **Hotels**: 3 premier properties across Delhi, Goa, and Bengaluru.
- **Rooms**: 20 inventory units spanning all 5 categories and statuses (Available, Occupied, Maintenance).
- **Customers**: 15 verified guest profiles with contact and address details.
- **Employees**: 10 staff profiles covering General Managers, Front Desk, Chefs, and Housekeepers.
- **Bookings**: 20 reservations across confirmed, pending, completed, and cancelled statuses.
- **Payments**: 20 transactions across multiple channels (UPI, Credit/Debit Cards, Net Banking, Cash).
- **Restaurants**: 3 on-site outlets covering North Indian, Goan Seafood, and Pan-Asian cuisines.
- **Food Items**: 15 culinary menu items across 5 food categories.
- **Hotel Services**: 8 guest amenities and recreation offerings.
- **Housekeeping**: 15 sanitation records tracking daily room inspections and assignments.

---

## 8. Representative SQL Queries

The following queries highlight the core DBMS techniques implemented in the application:

### Query A: Financial Reconciliation Subqueries (Dashboard KPIs)
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

### Query B: Multi-Table Joined Reservation Record
```sql
SELECT 
    b.booking_id,
    c.customer_name,
    c.email,
    r.room_number,
    r.room_type,
    h.hotel_name,
    b.check_in_date,
    b.check_out_date,
    b.booking_status,
    b.total_amount
FROM BOOKING b
INNER JOIN CUSTOMER c ON b.customer_id = c.customer_id
INNER JOIN ROOM r ON b.room_id = r.room_id
INNER JOIN HOTEL h ON r.hotel_id = h.hotel_id
ORDER BY b.booking_id DESC;
```

### Query C: Concurrency Overlap Prevention Verification
```sql
SELECT COUNT(*) AS overlap_count
FROM BOOKING
WHERE room_id = %s
  AND booking_status IN ('Confirmed', 'Completed')
  AND check_in_date < %s
  AND check_out_date > %s;
```

### Query D: Room Occupancy Rate Calculation
```sql
SELECT 
    COUNT(*) AS total_rooms,
    SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,
    SUM(CASE WHEN room_status = 'Available' THEN 1 ELSE 0 END) AS available_rooms,
    SUM(CASE WHEN room_status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_rooms,
    ROUND((SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS occupancy_percentage
FROM ROOM;
```

### Query E: Historical Monthly Revenue Trend
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

---

## 9. Verification & Testing Outcomes

All 12 automated unit and integration tests passed with 100% success rate:
- Configuration and default parameter validation: **PASS**
- Database DDL schema entities and constraint parsing: **PASS**
- Foreign key cascading and referential integrity check: **PASS**
- Deterministic seed record existence: **PASS**
- Graceful offline database handling: **PASS**
- `/health` endpoint JSON monitoring check: **PASS**
- Custom 404 page rendering on invalid routes: **PASS**
- Executive dashboard KPI and join rendering: **PASS**
- Multi-parameter room search and filtering: **PASS**
- Customer directory and lifetime spend calculation: **PASS**
- Payments ledger and grouped financial summaries: **PASS**
- Server-side date validation rejecting invalid check-out dates: **PASS**

---

## 10. Conclusion

The **Grand Luxe Hotel Management System** successfully fulfills all theoretical and practical requirements of the **CAM 5 Database Application** assignment.

By strictly adhering to Third Normal Form relational principles, enforcing SQL constraints at both the database and application levels, and coupling the backend directly to MySQL 8.0 without intermediate ORM layers, the project provides a clean, performant, and reliable demonstration of enterprise database design.
