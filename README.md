# Grand Luxe Hotel Management ERP Database Application
**College CAM 5 Assignment — Relational Database Management Systems**  
**Author**: B.Tech Computer Science & Engineering Student  
**Academic Year**: 2026  

---

## 1. Project Overview

The **Grand Luxe Hotel Management System** is a full-stack, enterprise-grade, database-driven web application designed to fulfill all requirements of the **CAM 5 Database Application** laboratory assignment.

The system manages multi-property hotel operations, room inventories, customer relationships, reservation schedules, multi-channel payment settlements, dining menus, guest amenities, human resources, and room housekeeping audits.

### Key Capabilities
- **Relational Integrity**: Complete schema in Third Normal Form (3NF) encompassing 10 interconnected entities in MySQL 8.0.
- **Advanced Querying**: Parameterized queries utilizing projection, multi-table `INNER JOIN` and `LEFT JOIN`, multi-condition `WHERE` filters, sorting whitelist protection, `GROUP BY`, and aggregate functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
- **Data Integrity & Concurrency**: Server-side transactional double-booking prevention ensuring no overlapping confirmed reservations for the same room.
- **Analytics & BI**: 12 dedicated business intelligence SQL queries computing room occupancy rate, monthly collected revenue trends, channel breakdowns, and VIP customer rankings.
- **Containerized Architecture**: Local orchestration via Docker Compose with health checks and persistent volume storage.

---

## 2. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend** | HTML5 / CSS3 | Modern Spec | Semantic markup, responsive sidebar ERP theme |
| **Templating** | Jinja2 | 3.1+ | Dynamic server-side UI rendering |
| **Backend** | Python Flask | 3.1+ | RESTful routing, input validation, transaction control |
| **Database** | MySQL Server | 8.0 | Relational storage, referential integrity, constraints |
| **DB Driver** | PyMySQL | 1.1+ | Pure Python MySQL client with dictionary cursors |
| **Charts** | Chart.js | 4.4+ | Dynamic client-side visualizations with fallback |
| **Orchestration** | Docker & Docker Compose | Compose v2+ | Isolated containerized execution & persistence |
| **Testing** | Pytest | 9.1+ | Automated unit, route, and schema verification |

---

## 3. Database Architecture

The database `hotel_management` contains 10 normalized tables with 114 deterministic sample records:

1. `HOTEL` (3 properties in New Delhi, Goa, Bengaluru)
2. `ROOM` (20 rooms with categories: Single, Double, Deluxe, Suite, Presidential Suite)
3. `CUSTOMER` (15 registered guest profiles)
4. `EMPLOYEE` (10 staff members across management, front desk, culinary, and housekeeping)
5. `BOOKING` (20 reservation records with dates, guest counts, and statuses)
6. `PAYMENT` (20 transactions across UPI, Credit Card, Debit Card, Net Banking, and Cash)
7. `RESTAURANT` (3 on-premise dining outlets)
8. `FOOD` (15 culinary dishes across Appetizers, Main Courses, Desserts, and Beverages)
9. `SERVICE` (8 hotel amenities including Spa, Airport Shuttle, and Conference Facilities)
10. `HOUSEKEEPING` (15 sanitation inspection and room cleaning records)

---

## 4. Quick Start with Docker Compose (Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on Windows, macOS, or Linux.
- Docker Compose v2+ enabled.

### Step 1: Clone or Navigate to Project
```bash
cd hotel-management-cam5
```

### Step 2: Environment Configuration
Copy the provided `.env.example` file to create `.env`:
```bash
# On Windows PowerShell
Copy-Item .env.example .env

# On Linux / macOS
cp .env.example .env
```

### Step 3: Start the Application Services
Run Docker Compose to build the Flask container and start MySQL 8.0:
```bash
docker compose up --build -d
```

### Step 4: Access the Application
Open your web browser and navigate to:
```
http://localhost:5000
```

### Step 5: View Logs
```bash
# View combined logs
docker compose logs -f

# View Flask web logs only
docker compose logs -f web

# View MySQL database logs only
docker compose logs -f db
```

### Step 6: Stop Containers
```bash
docker compose down
```

---

## 5. Local Python Development Setup (Alternative)

If running without Docker, you can run the Flask backend directly against a local MySQL instance:

### Step 1: Install Python Dependencies
```bash
python -m pip install -r requirements.txt
```

### Step 2: Initialize MySQL Database
Log into your local MySQL CLI as `root` and execute `database/init.sql`:
```bash
mysql -u root -p < database/init.sql
```

### Step 3: Configure Environment Variables
Set database connection parameters in your environment:
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="3306"
$env:DB_USER="hotel_admin"
$env:DB_PASSWORD="hotel_secure_pwd_2026"
$env:DB_NAME="hotel_management"
```

### Step 4: Run Flask Development Server
```bash
python app.py
```
Access at `http://localhost:5000`.

---

## 6. How to Reset the Database Safely

The database container uses a named Docker volume (`hotel_cam5_mysql_data`) for persistent data retention across restarts. To reset the database to a fresh state with clean seed records:

```bash
# 1. Stop containers and delete named volume
docker compose down -v

# 2. Restart services (init.sql will automatically re-seed)
docker compose up -d
```

---

## 7. Running the Test Suite

The project includes an automated test suite with **24 test cases** divided into Unit Tests (mocked) and Real MySQL Integration Tests:

### Run Tests Inside Docker Web Container (Full Live Integration Suite)
```bash
docker exec hotel_cam5_web python -m pytest tests/ -v
```

### Run Tests on Host Machine
```bash
# Set PYTHONPATH and execute pytest
python -m pytest tests/ -v
```

> **Note on Test Architecture**:
> - **Unit Tests** (`tests/test_routes.py`, `tests/test_database.py`): Mock database cursors to verify server-side input validation, error handling, date rejection, and template responses without touching real data.
> - **Integration Tests** (`tests/test_integration.py`): Execute directly against the live MySQL container to verify row-locking concurrency, double-booking rejection, check-in/check-out room status transitions, overpayment prevention, and referential integrity protection. All temporary test entities are cleaned up automatically after each test.

---

## 8. Application URL Directory

| Module | Route URL | Key Features |
|---|---|---|
| **Executive Dashboard** | `/` | Operational KPI cards (Live Occupancy Rate, Outstanding Balances, Today's Arrivals & Departures), recent bookings |
| **Room Inventory** | `/rooms/` | Search by room number, hotel, category, status, price range, and **Date-range Availability Filter** |
| **Add Room** | `/rooms/new` | Add new room with duplicate number check per property and status assignment |
| **Edit Room** | `/rooms/<id>/edit` | Update room category, nightly rate, and maintenance status |
| **Delete Room** | `/rooms/<id>/delete` | POST endpoint with referential integrity guard (blocks deletion if reservations exist) |
| **Customer Directory** | `/customers/` | Search by name/email/phone, aggregated booking counts, and lifetime spend |
| **Register Guest** | `/customers/new` | Register new guest with email uniqueness validation and contact formatting |
| **Customer Detail** | `/customers/<id>` | Full guest profile and history of stay reservations |
| **Edit Customer** | `/customers/<id>/edit` | Update profile with email duplicate prevention |
| **Delete Customer** | `/customers/<id>/delete` | POST endpoint with booking FK protection |
| **Reservations** | `/bookings/` | Filter by booking ID, guest, hotel, status, and check-in date range |
| **Reservation Detail** | `/bookings/<id>` | Invoiced vs Paid financial bar, Check-In, Check-Out, and Cancel action triggers |
| **New Reservation** | `/bookings/new` | Concurrency-protected booking (`SELECT ... FOR UPDATE`), date validation, price calculation |
| **Edit Reservation** | `/bookings/<id>/edit` | Modify stay dates, guest count, and room with overlap re-validation |
| **Check In Guest** | `/bookings/<id>/check-in` | POST endpoint: marks room `Occupied` upon guest arrival |
| **Check Out Guest** | `/bookings/<id>/check-out` | POST endpoint: marks room `Available`, sets status `Completed`, creates `Dirty` housekeeping task |
| **Cancel Reservation** | `/bookings/<id>/cancel` | POST endpoint: sets booking `Cancelled` and releases room back to `Available` |
| **Payments Ledger** | `/payments/` | Filter by status/channel/date, revenue totals, method breakdown table |
| **Record Payment** | `/payments/new` | Record payment against booking with balance validation and overpayment prevention |
| **Restaurants & Dining**| `/restaurants/` | Menu catalog joined with restaurant outlets, cuisine filters, price range filters |
| **Hotel Services** | `/services/` | Amenities catalog, keyword search, property filters, price sorting |
| **Staff Directory** | `/employees/` | Employee directory joined with hotels, designation filter, payroll averages |
| **Housekeeping Logs** | `/housekeeping/` | Sanitation logs joined with rooms and staff, inspection status filter |
| **SQL Analytics** | `/analytics/` | 14 advanced SQL reports, live occupancy percentage, monthly revenue trend, receivables audit |
| **System Health** | `/health` | JSON health check reporting database connection status |

---

## 9. Troubleshooting & FAQ

1. **Port 5000 is already in use**:
   Change the host port mapping in `compose.yaml` (e.g. `"5001:5000"`) and access `http://localhost:5001`.
2. **Database connection failed on startup**:
   The web service is configured with `condition: service_healthy` on MySQL. Ensure the database container healthcheck passes before accessing the app.
3. **Chart.js is not rendering**:
   If internet connectivity is restricted, a built-in fallback alert is rendered while all tabular numerical data remains fully accessible.
