from flask import Blueprint, render_template, request
from db.connection import query_all, query_one

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('/')
def list_employees():
    hotel_id = request.args.get('hotel_id', '').strip()
    designation = request.args.get('designation', '').strip()

    base_query = """
        SELECT 
            e.employee_id,
            e.employee_name,
            e.designation,
            e.salary,
            e.phone,
            h.hotel_id,
            h.hotel_name,
            h.location
        FROM EMPLOYEE e
        INNER JOIN HOTEL h ON e.hotel_id = h.hotel_id
        WHERE 1=1
    """
    params = []

    if hotel_id and hotel_id.isdigit():
        base_query += " AND e.hotel_id = %s"
        params.append(int(hotel_id))

    if designation:
        base_query += " AND e.designation = %s"
        params.append(designation)

    base_query += " ORDER BY h.hotel_name, e.employee_name ASC"

    employees = query_all(base_query, tuple(params))
    hotels = query_all("SELECT hotel_id, hotel_name FROM HOTEL ORDER BY hotel_name ASC")
    designations = query_all("SELECT DISTINCT designation FROM EMPLOYEE ORDER BY designation ASC")

    stats = query_one("""
        SELECT 
            COUNT(*) AS total_employees,
            COALESCE(AVG(salary), 0) AS avg_salary,
            COUNT(DISTINCT designation) AS total_roles
        FROM EMPLOYEE
    """) or {}

    return render_template(
        'employees.html',
        employees=employees,
        hotels=hotels,
        designations=designations,
        stats=stats,
        filters={'hotel_id': hotel_id, 'designation': designation}
    )
