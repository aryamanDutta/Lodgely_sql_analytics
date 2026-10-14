-- =============================================================================
-- CAM 5 Assignment: Hotel Management Database System
-- Database: hotel_management
-- Compatibility: MySQL 8.0+
-- Author: B.Tech Computer Science Student
-- Description: Complete schema, constraints, relationships, indexes, and seed data
-- =============================================================================

CREATE DATABASE IF NOT EXISTS hotel_management;
USE hotel_management;

-- -----------------------------------------------------------------------------
-- Drop tables in reverse dependency order if resetting
-- -----------------------------------------------------------------------------
DROP TABLE IF EXISTS HOUSEKEEPING;
DROP TABLE IF EXISTS FOOD;
DROP TABLE IF EXISTS RESTAURANT;
DROP TABLE IF EXISTS SERVICE;
DROP TABLE IF EXISTS PAYMENT;
DROP TABLE IF EXISTS BOOKING;
DROP TABLE IF EXISTS EMPLOYEE;
DROP TABLE IF EXISTS CUSTOMER;
DROP TABLE IF EXISTS ROOM;
DROP TABLE IF EXISTS HOTEL;

-- -----------------------------------------------------------------------------
-- 1. Table: HOTEL
-- -----------------------------------------------------------------------------
CREATE TABLE HOTEL (
    hotel_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_name VARCHAR(100) NOT NULL,
    location VARCHAR(200) NOT NULL,
    contact_number VARCHAR(20) NOT NULL,
    star_rating DECIMAL(2, 1) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_hotel_star_rating CHECK (star_rating >= 1.0 AND star_rating <= 5.0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 2. Table: ROOM
-- -----------------------------------------------------------------------------
CREATE TABLE ROOM (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL,
    room_number VARCHAR(10) NOT NULL,
    room_type VARCHAR(50) NOT NULL,
    price_per_night DECIMAL(10, 2) NOT NULL,
    room_status VARCHAR(20) NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_room_hotel FOREIGN KEY (hotel_id) REFERENCES HOTEL(hotel_id) ON DELETE CASCADE,
    CONSTRAINT uk_hotel_room UNIQUE (hotel_id, room_number),
    CONSTRAINT chk_room_price CHECK (price_per_night > 0),
    CONSTRAINT chk_room_status CHECK (room_status IN ('Available', 'Occupied', 'Maintenance')),
    CONSTRAINT chk_room_type CHECK (room_type IN ('Single', 'Double', 'Deluxe', 'Suite', 'Presidential Suite'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 3. Table: CUSTOMER
-- -----------------------------------------------------------------------------
CREATE TABLE CUSTOMER (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 4. Table: EMPLOYEE
-- -----------------------------------------------------------------------------
CREATE TABLE EMPLOYEE (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL,
    employee_name VARCHAR(100) NOT NULL,
    designation VARCHAR(50) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_employee_hotel FOREIGN KEY (hotel_id) REFERENCES HOTEL(hotel_id) ON DELETE CASCADE,
    CONSTRAINT chk_employee_salary CHECK (salary > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 5. Table: BOOKING
-- -----------------------------------------------------------------------------
CREATE TABLE BOOKING (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    number_of_guests INT NOT NULL DEFAULT 1,
    booking_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    total_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_booking_customer FOREIGN KEY (customer_id) REFERENCES CUSTOMER(customer_id) ON DELETE RESTRICT,
    CONSTRAINT fk_booking_room FOREIGN KEY (room_id) REFERENCES ROOM(room_id) ON DELETE RESTRICT,
    CONSTRAINT chk_booking_dates CHECK (check_out_date >= check_in_date),
    CONSTRAINT chk_booking_guests CHECK (number_of_guests > 0),
    CONSTRAINT chk_booking_status CHECK (booking_status IN ('Confirmed', 'Pending', 'Cancelled', 'Completed')),
    CONSTRAINT chk_booking_amount CHECK (total_amount >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 6. Table: PAYMENT
-- -----------------------------------------------------------------------------
CREATE TABLE PAYMENT (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    payment_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_booking FOREIGN KEY (booking_id) REFERENCES BOOKING(booking_id) ON DELETE CASCADE,
    CONSTRAINT chk_payment_amount CHECK (amount > 0),
    CONSTRAINT chk_payment_method CHECK (payment_method IN ('Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Cash')),
    CONSTRAINT chk_payment_status CHECK (payment_status IN ('Completed', 'Pending', 'Failed', 'Refunded'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 7. Table: RESTAURANT
-- -----------------------------------------------------------------------------
CREATE TABLE RESTAURANT (
    restaurant_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL,
    restaurant_name VARCHAR(100) NOT NULL,
    cuisine_type VARCHAR(50) NOT NULL,
    opening_hours VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_restaurant_hotel FOREIGN KEY (hotel_id) REFERENCES HOTEL(hotel_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 8. Table: FOOD
-- -----------------------------------------------------------------------------
CREATE TABLE FOOD (
    food_id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    food_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    availability VARCHAR(20) NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_food_restaurant FOREIGN KEY (restaurant_id) REFERENCES RESTAURANT(restaurant_id) ON DELETE CASCADE,
    CONSTRAINT chk_food_category CHECK (category IN ('Appetizer', 'Main Course', 'Dessert', 'Beverage', 'Snacks')),
    CONSTRAINT chk_food_price CHECK (price > 0),
    CONSTRAINT chk_food_availability CHECK (availability IN ('Available', 'Out of Stock'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 9. Table: SERVICE
-- -----------------------------------------------------------------------------
CREATE TABLE SERVICE (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_service_hotel FOREIGN KEY (hotel_id) REFERENCES HOTEL(hotel_id) ON DELETE CASCADE,
    CONSTRAINT chk_service_price CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- 10. Table: HOUSEKEEPING
-- -----------------------------------------------------------------------------
CREATE TABLE HOUSEKEEPING (
    housekeeping_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    room_id INT NOT NULL,
    cleaning_date DATE NOT NULL,
    cleaning_status VARCHAR(30) NOT NULL DEFAULT 'Pending Inspection',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_housekeeping_employee FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id) ON DELETE CASCADE,
    CONSTRAINT fk_housekeeping_room FOREIGN KEY (room_id) REFERENCES ROOM(room_id) ON DELETE CASCADE,
    CONSTRAINT chk_housekeeping_status CHECK (cleaning_status IN ('Clean', 'In Progress', 'Pending Inspection', 'Dirty'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- -----------------------------------------------------------------------------
-- Indexes for performance optimization on common filters & joins
-- -----------------------------------------------------------------------------
CREATE INDEX idx_room_hotel_status ON ROOM(hotel_id, room_status);
CREATE INDEX idx_room_type ON ROOM(room_type);
CREATE INDEX idx_room_price ON ROOM(price_per_night);
CREATE INDEX idx_booking_customer ON BOOKING(customer_id);
CREATE INDEX idx_booking_room ON BOOKING(room_id);
CREATE INDEX idx_booking_dates ON BOOKING(check_in_date, check_out_date);
CREATE INDEX idx_booking_status ON BOOKING(booking_status);
CREATE INDEX idx_payment_booking ON PAYMENT(booking_id);
CREATE INDEX idx_payment_status ON PAYMENT(payment_status);
CREATE INDEX idx_payment_date ON PAYMENT(payment_date);
CREATE INDEX idx_food_restaurant_category ON FOOD(restaurant_id, category);
CREATE INDEX idx_housekeeping_room ON HOUSEKEEPING(room_id);
CREATE INDEX idx_housekeeping_employee ON HOUSEKEEPING(employee_id);
CREATE INDEX idx_housekeeping_status ON HOUSEKEEPING(cleaning_status);

-- =============================================================================
-- SAMPLE DATA INSERTION (Deterministic Seed Records)
-- =================================----------------============================

-- 1. Insert 3 Hotels
INSERT INTO HOTEL (hotel_id, hotel_name, location, contact_number, star_rating) VALUES
(1, 'The Grand Horizon Hotel & Suites', 'Connaught Place, New Delhi', '+91 11 2341 5678', 4.8),
(2, 'Seaside Royal Palace Resort', 'Candolim Beach, Goa', '+91 832 248 9900', 4.5),
(3, 'Emerald Valley Heritage Hotel', 'M.G. Road, Bengaluru', '+91 80 4123 7788', 4.2);

-- 2. Insert 20 Rooms across the 3 Hotels
INSERT INTO ROOM (room_id, hotel_id, room_number, room_type, price_per_night, room_status) VALUES
-- Hotel 1 (New Delhi)
(1,  1, '101', 'Single',             2500.00, 'Available'),
(2,  1, '102', 'Double',             4200.00, 'Occupied'),
(3,  1, '201', 'Deluxe',             6500.00, 'Available'),
(4,  1, '202', 'Deluxe',             6800.00, 'Occupied'),
(5,  1, '301', 'Suite',             11500.00, 'Available'),
(6,  1, '302', 'Presidential Suite', 24000.00, 'Occupied'),
(7,  1, '103', 'Single',             2600.00, 'Maintenance'),

-- Hotel 2 (Goa)
(8,  2, 'G-101', 'Single',           3200.00, 'Available'),
(9,  2, 'G-102', 'Double',           5400.00, 'Occupied'),
(10, 2, 'G-201', 'Deluxe',           7800.00, 'Available'),
(11, 2, 'G-202', 'Deluxe',           8200.00, 'Occupied'),
(12, 2, 'G-301', 'Suite',           14500.00, 'Available'),
(13, 2, 'G-302', 'Presidential Suite', 28500.00, 'Available'),
(14, 2, 'G-103', 'Double',           5100.00, 'Maintenance'),

-- Hotel 3 (Bengaluru)
(15, 3, 'B-101', 'Single',           2200.00, 'Available'),
(16, 3, 'B-102', 'Double',           3900.00, 'Occupied'),
(17, 3, 'B-201', 'Deluxe',           5900.00, 'Available'),
(18, 3, 'B-202', 'Deluxe',           6200.00, 'Available'),
(19, 3, 'B-301', 'Suite',            9800.00, 'Occupied'),
(20, 3, 'B-302', 'Suite',           10500.00, 'Available');

-- 3. Insert 15 Customers
INSERT INTO CUSTOMER (customer_id, customer_name, email, phone, address) VALUES
(1,  'Aarav Sharma',     'aarav.sharma@example.com',     '+91 98112 34567', '42 Golf Links, New Delhi'),
(2,  'Priya Nair',       'priya.nair@example.com',       '+91 98220 54321', '12 Marine Drive, Mumbai'),
(3,  'Rohan Mehta',      'rohan.mehta@example.com',      '+91 98331 67890', '78 Sector 15, Gurugram'),
(4,  'Ananya Iyer',      'ananya.iyer@example.com',      '+91 98442 89012', '104 Indiranagar, Bengaluru'),
(5,  'Vikram Malhotra',  'vikram.m@example.com',         '+91 98553 12345', '15 Alipore Road, Kolkata'),
(6,  'Neha Patel',       'neha.patel@example.com',       '+91 98664 23456', '55 Navrangpura, Ahmedabad'),
(7,  'Kabir Sengupta',   'kabir.sengupta@example.com',   '+91 98775 34567', '89 Ballygunge Place, Kolkata'),
(8,  'Diya Kapoor',      'diya.kapoor@example.com',      '+91 98886 45678', '201 Pali Hill, Bandra, Mumbai'),
(9,  'Aditya Verma',     'aditya.verma@example.com',     '+91 98997 56789', '34 Civil Lines, Jaipur'),
(10, 'Ishaan Joshi',     'ishaan.joshi@example.com',     '+91 98108 67890', '77 Kothrud, Pune'),
(11, 'Sneha Rao',        'sneha.rao@example.com',        '+91 98219 78901', '19 Jayanagar, Bengaluru'),
(12, 'Arjun Reddy',      'arjun.reddy@example.com',      '+91 98320 89012', '63 Jubilee Hills, Hyderabad'),
(13, 'Meera Nambiar',    'meera.nambiar@example.com',    '+91 98431 90123', '28 Panampilly Nagar, Kochi'),
(14, 'Tanvi Kulkarni',   'tanvi.kulkarni@example.com',   '+91 98542 01234', '84 FC Road, Pune'),
(15, 'Siddharth Rao',    'siddharth.rao@example.com',    '+91 98653 12345', '112 Anna Nagar, Chennai');

-- 4. Insert 10 Employees
INSERT INTO EMPLOYEE (employee_id, hotel_id, employee_name, designation, salary, phone) VALUES
(1,  1, 'Rajesh Khanna',     'General Manager',    95000.00, '+91 97111 00001'),
(2,  1, 'Sunita Verma',      'Front Desk Manager', 55000.00, '+91 97111 00002'),
(3,  1, 'Manoj Kumar',       'Housekeeper',        28000.00, '+91 97111 00003'),
(4,  1, 'Ramesh Babu',       'Executive Chef',     72000.00, '+91 97111 00004'),
(5,  2, 'Anthony Dsouza',    'Hotel Manager',      90000.00, '+91 97222 00005'),
(6,  2, 'Maria Fernandes',   'Front Desk Agent',   42000.00, '+91 97222 00006'),
(7,  2, 'Suresh Gawde',      'Housekeeper',        27000.00, '+91 97222 00007'),
(8,  3, 'Deepak Hegde',      'General Manager',    88000.00, '+91 97333 00008'),
(9,  3, 'Kavita Swaminathan','Housekeeper',        29000.00, '+91 97333 00009'),
(10, 3, 'Ganesh Prasad',     'Sous Chef',          58000.00, '+91 97333 00010');

-- 5. Insert 20 Bookings
INSERT INTO BOOKING (booking_id, customer_id, room_id, check_in_date, check_out_date, number_of_guests, booking_status, total_amount) VALUES
(1,  1,  2,  '2026-10-10', '2026-10-15', 2, 'Confirmed',  21000.00), -- 5 nights * 4200
(2,  2,  4,  '2026-10-12', '2026-10-16', 2, 'Confirmed',  27200.00), -- 4 nights * 6800
(3,  3,  6,  '2026-10-14', '2026-10-18', 3, 'Confirmed',  96000.00), -- 4 nights * 24000
(4,  4,  9,  '2026-10-11', '2026-10-17', 2, 'Confirmed',  32400.00), -- 6 nights * 5400
(5,  5,  11, '2026-10-13', '2026-10-17', 2, 'Confirmed',  32800.00), -- 4 nights * 8200
(6,  6,  16, '2026-10-10', '2026-10-14', 2, 'Confirmed',  15600.00), -- 4 nights * 3900
(7,  7,  19, '2026-10-12', '2026-10-15', 2, 'Confirmed',  29400.00), -- 3 nights * 9800
(8,  8,  1,  '2026-10-20', '2026-10-22', 1, 'Pending',     5000.00), -- 2 nights * 2500
(9,  9,  3,  '2026-10-25', '2026-10-28', 2, 'Pending',    19500.00), -- 3 nights * 6500
(10, 10, 8,  '2026-10-22', '2026-10-25', 1, 'Pending',     9600.00), -- 3 nights * 3200
(11, 11, 10, '2026-10-24', '2026-10-27', 2, 'Pending',    23400.00), -- 3 nights * 7800
(12, 12, 15, '2026-10-21', '2026-10-24', 1, 'Pending',     6600.00), -- 3 nights * 2200
(13, 1,  5,  '2026-09-01', '2026-09-05', 2, 'Completed',  46000.00), -- 4 nights * 11500
(14, 2,  12, '2026-09-10', '2026-09-14', 2, 'Completed',  58000.00), -- 4 nights * 14500
(15, 3,  17, '2026-09-15', '2026-09-18', 2, 'Completed',  17700.00), -- 3 nights * 5900
(16, 13, 18, '2026-09-20', '2026-09-23', 2, 'Completed',  18600.00), -- 3 nights * 6200
(17, 14, 20, '2026-09-25', '2026-09-27', 2, 'Completed',  21000.00), -- 2 nights * 10500
(18, 15, 1,  '2026-09-12', '2026-09-14', 1, 'Cancelled',   5000.00),
(19, 4,  13, '2026-11-01', '2026-11-05', 3, 'Confirmed', 114000.00), -- 4 nights * 28500
(20, 5,  7,  '2026-10-05', '2026-10-08', 1, 'Cancelled',   7800.00);

-- 6. Insert 20 Payments
INSERT INTO PAYMENT (payment_id, booking_id, payment_date, amount, payment_method, payment_status) VALUES
(1,  1,  '2026-10-10 10:15:00', 21000.00, 'UPI',         'Completed'),
(2,  2,  '2026-10-12 11:30:00', 27200.00, 'Credit Card', 'Completed'),
(3,  3,  '2026-10-14 09:00:00', 96000.00, 'Net Banking', 'Completed'),
(4,  4,  '2026-10-11 14:45:00', 32400.00, 'Debit Card',  'Completed'),
(5,  5,  '2026-10-13 16:20:00', 32800.00, 'UPI',         'Completed'),
(6,  6,  '2026-10-10 18:00:00', 15600.00, 'Cash',        'Completed'),
(7,  7,  '2026-10-12 12:10:00', 29400.00, 'Credit Card', 'Completed'),
(8,  8,  '2026-10-14 10:00:00',  5000.00, 'UPI',         'Pending'),
(9,  9,  '2026-10-14 11:00:00', 19500.00, 'Net Banking', 'Pending'),
(10, 10, '2026-10-14 12:30:00',  9600.00, 'Debit Card',  'Pending'),
(11, 11, '2026-10-14 13:00:00', 23400.00, 'UPI',         'Pending'),
(12, 12, '2026-10-14 14:15:00',  6600.00, 'Credit Card', 'Pending'),
(13, 13, '2026-09-01 09:30:00', 46000.00, 'Credit Card', 'Completed'),
(14, 14, '2026-09-10 15:00:00', 58000.00, 'Net Banking', 'Completed'),
(15, 15, '2026-09-15 11:45:00', 17700.00, 'UPI',         'Completed'),
(16, 16, '2026-09-20 16:10:00', 18600.00, 'Debit Card',  'Completed'),
(17, 17, '2026-09-25 10:20:00', 21000.00, 'Cash',        'Completed'),
(18, 18, '2026-09-12 08:30:00',  5000.00, 'UPI',         'Refunded'),
(19, 19, '2026-10-14 15:00:00', 114000.00,'Credit Card', 'Completed'),
(20, 20, '2026-10-05 09:00:00',  7800.00, 'Net Banking', 'Failed');

-- 7. Insert 3 Restaurants
INSERT INTO RESTAURANT (restaurant_id, hotel_id, restaurant_name, cuisine_type, opening_hours) VALUES
(1, 1, 'The Grand Dine Bistro', 'North Indian & Continental', '07:00 AM - 11:30 PM'),
(2, 2, 'Spice Symphony Shack',  'Goan & Seafood Specialities', '08:00 AM - 12:00 AM'),
(3, 3, 'Emerald Garden Cafe',   'South Indian & Pan-Asian',   '06:30 AM - 11:00 PM');

-- 8. Insert 15 Food Items
INSERT INTO FOOD (food_id, restaurant_id, food_name, category, price, availability) VALUES
-- Restaurant 1 (Grand Dine Bistro)
(1,  1, 'Paneer Tikka Angara',       'Appetizer',    380.00, 'Available'),
(2,  1, 'Murgh Makhani (Butter Chicken)', 'Main Course', 560.00, 'Available'),
(3,  1, 'Dal Makhani Heritage',      'Main Course',  420.00, 'Available'),
(4,  1, 'Gulab Jamun with Rabri',    'Dessert',      240.00, 'Available'),
(5,  1, 'Fresh Lime Soda',           'Beverage',     150.00, 'Available'),

-- Restaurant 2 (Spice Symphony Shack)
(6,  2, 'Crispy Calamari Peri-Peri', 'Appetizer',    490.00, 'Available'),
(7,  2, 'Goan Prawn Curry with Rice', 'Main Course', 650.00, 'Available'),
(8,  2, 'Kingfish Rava Fry',         'Appetizer',    580.00, 'Available'),
(9,  2, 'Bebinca with Vanilla Scoop','Dessert',      290.00, 'Available'),
(10, 2, 'Tender Coconut Cooler',     'Beverage',     180.00, 'Available'),

-- Restaurant 3 (Emerald Garden Cafe)
(11, 3, 'Guntur Chilli Paneer',      'Appetizer',    340.00, 'Available'),
(12, 3, 'Mysore Masala Dosa Platter','Snacks',       260.00, 'Available'),
(13, 3, 'Thai Green Curry Bowl',     'Main Course',  510.00, 'Available'),
(14, 3, 'Filter Kaapi Tiramisu',     'Dessert',      280.00, 'Available'),
(15, 3, 'Madras Special Filter Coffee','Beverage',   120.00, 'Out of Stock');

-- 9. Insert 8 Hotel Services
INSERT INTO SERVICE (service_id, hotel_id, service_name, description, price) VALUES
(1, 1, 'Airport Chauffeured Shuttle', 'Direct executive luxury airport pickup and drop-off service.', 1500.00),
(2, 1, 'Ayurvedic Spa & Wellness',    'Traditional full-body relaxation therapy and steam bath (60 mins).', 2800.00),
(3, 1, 'Express Laundry & Pressing',  'Same-day washing, dry cleaning, and steaming service.', 650.00),
(4, 2, 'Scuba Diving & Watersports',  'Certified beginner diving experience with certified instructors.', 3500.00),
(5, 2, 'Beachside Candlelight Dinner','Curated 4-course dinner set under the stars with live acoustic music.', 4500.00),
(6, 2, 'Scooter & Bike Rental',       'Daily geared/automatic two-wheeler rental with helmets included.', 600.00),
(7, 3, 'Executive Conference Hall',   'High-tech meeting room with projector, video conferencing & audio.', 8000.00),
(8, 3, '24/7 Premium High-Speed WiFi','Gigabit speed unlimited internet access for conference and work.', 0.00);

-- 10. Insert 15 Housekeeping Records
INSERT INTO HOUSEKEEPING (housekeeping_id, employee_id, room_id, cleaning_date, cleaning_status) VALUES
(1,  3, 1,  '2026-10-14', 'Clean'),
(2,  3, 2,  '2026-10-14', 'In Progress'),
(3,  3, 3,  '2026-10-13', 'Clean'),
(4,  3, 4,  '2026-10-14', 'Dirty'),
(5,  3, 5,  '2026-10-14', 'Clean'),
(6,  3, 6,  '2026-10-14', 'Pending Inspection'),
(7,  3, 7,  '2026-10-12', 'Dirty'),
(8,  7, 8,  '2026-10-14', 'Clean'),
(9,  7, 9,  '2026-10-14', 'In Progress'),
(10, 7, 10, '2026-10-13', 'Clean'),
(11, 7, 11, '2026-10-14', 'Pending Inspection'),
(12, 7, 14, '2026-10-11', 'Dirty'),
(13, 9, 15, '2026-10-14', 'Clean'),
(14, 9, 16, '2026-10-14', 'In Progress'),
(15, 9, 19, '2026-10-14', 'Dirty');
