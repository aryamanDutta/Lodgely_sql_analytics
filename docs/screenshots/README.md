# Application Screenshots Guide — CAM 5 Submission

As specified in the assignment guidelines, screenshots must be genuine captures of the running web application connected to the MySQL 8.0 database, rather than static mockups.

## How to Capture the Screenshots

1. **Start the Application Stack**:
   Ensure Docker Desktop is open and run:
   ```bash
   docker compose up -d
   ```
2. **Access the Web Interface**:
   Open Google Chrome, Edge, or Firefox and go to:
   ```
   http://localhost:5000
   ```
3. **Capture and Save the 10 Required Screens in `docs/screenshots/`**:

| # | Required Screenshot | URL to Visit | Elements to Include | Recommended Filename |
|---|---|---|---|---|
| **1** | Main Dashboard | `http://localhost:5000/` | KPI cards, Booking status donut chart, Room types bar chart, recent bookings table | `01_main_dashboard.png` |
| **2** | Room Inventory Listing | `http://localhost:5000/rooms/` | Full room catalog table with hotel names, locations, categories, and prices | `02_room_listing.png` |
| **3** | Room Filtering in Action | `http://localhost:5000/rooms/?room_status=Available&min_price=2000&max_price=8000` | Filter form with criteria filled and filtered table results | `03_room_filtering.png` |
| **4** | Customer Directory / Search | `http://localhost:5000/customers/` | Customer list showing guest names, emails, phones, and lifetime spend sums | `04_customer_directory.png` |
| **5** | Booking Reservations Listing | `http://localhost:5000/bookings/` | Reservation table with guest names, hotel names, room numbers, dates, and statuses | `05_booking_listing.png` |
| **6** | Booking Detailed Record | `http://localhost:5000/bookings/1` | Joined customer details, room details, hotel location, and payment ledger entries | `06_booking_detail.png` |
| **7** | Payment Ledger & Breakdown | `http://localhost:5000/payments/` | Financial summary cards, payment transactions table, and channel volume breakdown | `07_payment_ledger.png` |
| **8** | Restaurant & Culinary Menu | `http://localhost:5000/restaurants/` | Menu items table joined with outlet names, hotels, cuisine types, and availability | `08_restaurant_menu.png` |
| **9** | SQL Analytics & Occupancy | `http://localhost:5000/analytics/` | Occupancy percentage card, average booking value, and monthly revenue chart | `09_sql_analytics.png` |
| **10** | Monthly Revenue Trend / BI | `http://localhost:5000/analytics/` (scrolled) | Monthly revenue line chart and top 5 most booked rooms table | `10_analytics_charts.png` |

---

## Tip for Clean Academic Screenshots
- Use `Ctrl + Shift + S` or the Windows Snipping Tool (`Win + Shift + S`) to capture clean, full-window screenshots.
- Ensure the top bar showing `MySQL 8.0 Connected` is visible to verify live database connectivity to your faculty.
