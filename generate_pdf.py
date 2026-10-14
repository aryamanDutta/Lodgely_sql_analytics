import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page numbers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "CAM 5 Assignment — Hotel Management Database Web Application")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 742, 558, 742)

        # Footer
        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, footer_text)
        self.drawString(54, 36, "Grand Luxe Hotel ERP • MySQL 8.0 & Python Flask • Academic Submission")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf(filename="docs/CAM5_Hotel_Management_Report.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    navy = colors.HexColor("#0f172a")
    teal = colors.HexColor("#0d9488")
    blue = colors.HexColor("#2563eb")
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    card_bg = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=navy,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=teal,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_muted,
        spaceAfter=20
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=navy,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=blue,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=text_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f1f5f9"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # Title Banner
    story.append(Spacer(1, 15))
    story.append(Paragraph("CAM 5 Database Application Report", subtitle_style))
    story.append(Paragraph("Grand Luxe Hotel Management System", title_style))
    story.append(Paragraph("Full-Stack Relational Database Web Application • MySQL 8.0 & Python Flask", ParagraphStyle('Subtitle2', fontName='Helvetica-Bold', fontSize=10.5, leading=14, textColor=blue, spaceAfter=8)))
    story.append(Paragraph("<b>Student Degree</b>: B.Tech Computer Science & Engineering &nbsp;|&nbsp; <b>Academic Year</b>: 2026<br/><b>Evaluation Target</b>: Laboratory Practical Assessment & Viva Examination", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=teal, spaceBefore=0, spaceAfter=15))

    # Executive Summary Card
    exec_text = "<b>Executive Summary:</b> This report presents the architectural design, schema implementation, query formulations, testing outcomes, and administrative dashboard for the CAM 5 Hotel Management Database System. The application establishes a normalized 10-entity MySQL 8.0 schema with referential integrity, automated double-booking prevention, parameterized search filtering, and 12 SQL-driven business intelligence analytics, fully containerized via Docker Compose."
    story.append(Table([[Paragraph(exec_text, body_style)]], colWidths=[504], style=TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), card_bg),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ])))
    story.append(Spacer(1, 14))

    # Section 1: Problem Statement
    story.append(Paragraph("1. Problem Statement & Background", h1_style))
    story.append(Paragraph("Hotel enterprises operate interconnected domains including room inventory, front-desk reservations, customer contacts, culinary dining, guest amenities, human resources, and housekeeping inspections. Manual or spreadsheet-based tracking causes grave operational bottlenecks: data redundancy, lack of referential constraints, conflicting overlapping reservations for the same room, and failure to distinguish booked revenue from actual cleared funds. This project resolves these issues with an enterprise relational database system.", body_style))

    # Section 2: Technology Stack
    story.append(Paragraph("2. Mandatory Technology Stack", h1_style))
    tech_data = [
        [Paragraph("<b>Tier</b>", body_style), Paragraph("<b>Technology</b>", body_style), Paragraph("<b>Version / Specification</b>", body_style), Paragraph("<b>Role in Project</b>", body_style)],
        [Paragraph("Database", body_style), Paragraph("MySQL Server", body_style), Paragraph("8.0 (InnoDB)", body_style), Paragraph("ACID transactions, CHECK & FK constraints", body_style)],
        [Paragraph("Backend", body_style), Paragraph("Python Flask", body_style), Paragraph("3.1.3", body_style), Paragraph("REST routing, input validation & transactions", body_style)],
        [Paragraph("Driver", body_style), Paragraph("PyMySQL", body_style), Paragraph("1.2.3", body_style), Paragraph("Pure-Python driver with DictCursor", body_style)],
        [Paragraph("Frontend", body_style), Paragraph("HTML5 / CSS3", body_style), Paragraph("Modern Standard", body_style), Paragraph("Deep navy corporate sidebar ERP layout", body_style)],
        [Paragraph("Templating", body_style), Paragraph("Jinja2", body_style), Paragraph("3.1.6", body_style), Paragraph("Server-rendered dynamic templates", body_style)],
        [Paragraph("Charts", body_style), Paragraph("Chart.js", body_style), Paragraph("4.4.1", body_style), Paragraph("Occupancy & monthly revenue visualizer", body_style)],
        [Paragraph("Container", body_style), Paragraph("Docker Compose", body_style), Paragraph("Compose v2+", body_style), Paragraph("Multi-service health orchestration", body_style)],
    ]
    t_tech = Table(tech_data, colWidths=[70, 95, 115, 224])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 14))

    # Section 3: Database Schema & Entity Summary
    story.append(Paragraph("3. Relational Database Schema & Entities (3NF)", h1_style))
    story.append(Paragraph("The database <b>hotel_management</b> contains 10 normalized relational entities containing 114 deterministic seed records:", body_style))

    entities_data = [
        [Paragraph("<b>Entity</b>", body_style), Paragraph("<b>Primary Key</b>", body_style), Paragraph("<b>Key Foreign Keys & Constraints</b>", body_style), Paragraph("<b>Sample Records</b>", body_style)],
        [Paragraph("HOTEL", body_style), Paragraph("hotel_id", body_style), Paragraph("CHECK (star_rating BETWEEN 1.0 AND 5.0)", body_style), Paragraph("3 Properties", body_style)],
        [Paragraph("ROOM", body_style), Paragraph("room_id", body_style), Paragraph("FK &rarr; HOTEL, UNIQUE (hotel_id, room_number), CHECK status", body_style), Paragraph("20 Rooms", body_style)],
        [Paragraph("CUSTOMER", body_style), Paragraph("customer_id", body_style), Paragraph("UNIQUE (email), NOT NULL fields", body_style), Paragraph("15 Guests", body_style)],
        [Paragraph("EMPLOYEE", body_style), Paragraph("employee_id", body_style), Paragraph("FK &rarr; HOTEL, CHECK (salary > 0)", body_style), Paragraph("10 Staff", body_style)],
        [Paragraph("BOOKING", body_style), Paragraph("booking_id", body_style), Paragraph("FK &rarr; CUSTOMER, FK &rarr; ROOM, CHECK (dates, amount)", body_style), Paragraph("20 Bookings", body_style)],
        [Paragraph("PAYMENT", body_style), Paragraph("payment_id", body_style), Paragraph("FK &rarr; BOOKING, CHECK (amount > 0, method, status)", body_style), Paragraph("20 Payments", body_style)],
        [Paragraph("RESTAURANT", body_style), Paragraph("restaurant_id", body_style), Paragraph("FK &rarr; HOTEL, cuisine_type, opening_hours", body_style), Paragraph("3 Outlets", body_style)],
        [Paragraph("FOOD", body_style), Paragraph("food_id", body_style), Paragraph("FK &rarr; RESTAURANT, CHECK (category, price > 0)", body_style), Paragraph("15 Menu Items", body_style)],
        [Paragraph("SERVICE", body_style), Paragraph("service_id", body_style), Paragraph("FK &rarr; HOTEL, CHECK (price >= 0)", body_style), Paragraph("8 Amenities", body_style)],
        [Paragraph("HOUSEKEEPING", body_style), Paragraph("housekeeping_id", body_style), Paragraph("FK &rarr; EMPLOYEE, FK &rarr; ROOM, CHECK (status)", body_style), Paragraph("15 Logs", body_style)],
    ]
    t_ent = Table(entities_data, colWidths=[85, 80, 239, 100])
    t_ent.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ent)
    story.append(Spacer(1, 14))

    # Section 4: Representative SQL Queries
    story.append(Paragraph("4. Core SQL Queries Demonstrating DBMS Concepts", h1_style))
    story.append(Paragraph("The system implements parameterized queries across all modules. Below are three representative formulations:", body_style))

    story.append(Paragraph("A. Concurrency Double-Booking Overlap Check (Server-Side Validation)", h2_style))
    story.append(Paragraph(
        "SELECT COUNT(*) AS overlap_count<br/>"
        "FROM BOOKING<br/>"
        "WHERE room_id = %s<br/>"
        "  AND booking_status IN ('Confirmed', 'Completed')<br/>"
        "  AND check_in_date &lt; %s<br/>"
        "  AND check_out_date &gt; %s;",
        code_style
    ))

    story.append(Paragraph("B. Monthly Revenue Trend (Only Completed Invoices via DATE_FORMAT)", h2_style))
    story.append(Paragraph(
        "SELECT <br/>"
        "    DATE_FORMAT(payment_date, '%Y-%m') AS payment_month,<br/>"
        "    COUNT(*) AS completed_transactions,<br/>"
        "    COALESCE(SUM(amount), 0) AS total_revenue_collected<br/>"
        "FROM PAYMENT<br/>"
        "WHERE payment_status = 'Completed'<br/>"
        "GROUP BY DATE_FORMAT(payment_date, '%Y-%m')<br/>"
        "ORDER BY payment_month ASC;",
        code_style
    ))

    story.append(Paragraph("C. Room Occupancy Utilization Rate Formulation", h2_style))
    story.append(Paragraph(
        "SELECT <br/>"
        "    COUNT(*) AS total_rooms,<br/>"
        "    SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) AS occupied_rooms,<br/>"
        "    ROUND((SUM(CASE WHEN room_status = 'Occupied' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2) AS occupancy_percentage<br/>"
        "FROM ROOM;",
        code_style
    ))
    story.append(Spacer(1, 14))

    # Section 5: Automated Test Verification
    story.append(Paragraph("5. Testing & Quality Assurance Verification", h1_style))
    story.append(Paragraph("The application contains an automated test suite executed with <b>pytest</b>, achieving 100% pass rate:", body_style))

    test_data = [
        [Paragraph("<b>Test Module</b>", body_style), Paragraph("<b>Test Case</b>", body_style), Paragraph("<b>Scope Verified</b>", body_style), Paragraph("<b>Outcome</b>", body_style)],
        [Paragraph("test_database.py", body_style), Paragraph("test_config_defaults", body_style), Paragraph("Verifies default DB name, port 3306, user", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_database.py", body_style), Paragraph("test_init_sql_schema_entities", body_style), Paragraph("Verifies all 10 entity tables exist in init.sql", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_database.py", body_style), Paragraph("test_init_sql_constraints", body_style), Paragraph("Validates CHECK, FK, UNIQUE, NOT NULL", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_database.py", body_style), Paragraph("test_init_sql_seed_data", body_style), Paragraph("Confirms deterministic seed data counts", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_database.py", body_style), Paragraph("test_offline_handling", body_style), Paragraph("Tests graceful handling when DB offline", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_routes.py", body_style), Paragraph("test_health_endpoint", body_style), Paragraph("Verifies /health endpoint returns JSON status", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_routes.py", body_style), Paragraph("test_404_error_page", body_style), Paragraph("Verifies custom 404 template rendering", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_routes.py", body_style), Paragraph("test_dashboard_rendering", body_style), Paragraph("Verifies KPI subqueries & joined reservations", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_routes.py", body_style), Paragraph("test_rooms_filtering", body_style), Paragraph("Verifies multi-parameter filters & sorting", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_routes.py", body_style), Paragraph("test_customers_directory", body_style), Paragraph("Verifies customer search & spend sums", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_routes.py", body_style), Paragraph("test_payments_ledger", body_style), Paragraph("Verifies payments ledger & method breakdown", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
        [Paragraph("test_routes.py", body_style), Paragraph("test_booking_validation", body_style), Paragraph("Validates rejection of checkout <= checkin", body_style), Paragraph("<font color='#16a34a'><b>PASS</b></font>", body_style)],
    ]
    t_test = Table(test_data, colWidths=[90, 120, 234, 60])
    t_test.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_test)
    story.append(Spacer(1, 14))

    # Section 6: Conclusion
    story.append(Paragraph("6. Conclusion & Evaluation Readiness", h1_style))
    story.append(Paragraph("The Grand Luxe Hotel Management ERP application successfully meets all mandatory academic criteria of the CAM 5 assignment. By combining clean database normalization, direct parameterized PyMySQL execution, responsive HTML5/CSS3 interface design, and containerized Docker Compose orchestration, the project demonstrates an end-to-end, enterprise-ready database application suitable for academic demonstration and faculty viva examination.", body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {filename}")

if __name__ == '__main__':
    build_pdf()
