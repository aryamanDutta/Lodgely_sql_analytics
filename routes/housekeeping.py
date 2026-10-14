from flask import Blueprint, render_template, request
from db.connection import query_all

housekeeping_bp = Blueprint('housekeeping', __name__, url_prefix='/housekeeping')

@housekeeping_bp.route('/')
def list_housekeeping():
    room_number = request.args.get('room_number', '').strip()
    employee_id = request.args.get('employee_id', '').strip()
    cleaning_date = request.args.get('cleaning_date', '').strip()
    cleaning_status = request.args.get('cleaning_status', '').strip()

    base_query = """
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
        WHERE 1=1
    """
    params = []

    if room_number:
        base_query += " AND r.room_number LIKE %s"
        params.append(f"%{room_number}%")

    if employee_id and employee_id.isdigit():
        base_query += " AND e.employee_id = %s"
        params.append(int(employee_id))

    if cleaning_date:
        base_query += " AND hk.cleaning_date = %s"
        params.append(cleaning_date)

    if cleaning_status:
        base_query += " AND hk.cleaning_status = %s"
        params.append(cleaning_status)

    base_query += " ORDER BY hk.cleaning_date DESC, hk.housekeeping_id DESC"

    records = query_all(base_query, tuple(params))
    employees = query_all("SELECT employee_id, employee_name FROM EMPLOYEE WHERE designation = 'Housekeeper' ORDER BY employee_name ASC")
    statuses = ['Clean', 'In Progress', 'Pending Inspection', 'Dirty']

    return render_template(
        'housekeeping.html',
        records=records,
        employees=employees,
        statuses=statuses,
        filters={
            'room_number': room_number,
            'employee_id': employee_id,
            'cleaning_date': cleaning_date,
            'cleaning_status': cleaning_status
        }
    )
