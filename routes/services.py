from flask import Blueprint, render_template, request
from db.connection import query_all

services_bp = Blueprint('services', __name__, url_prefix='/services')

@services_bp.route('/')
def list_services():
    search = request.args.get('search', '').strip()
    hotel_id = request.args.get('hotel_id', '').strip()
    sort_by = request.args.get('sort_by', 'service_name').strip()
    order = request.args.get('order', 'asc').strip().lower()

    valid_sorts = {
        'service_name': 's.service_name',
        'price': 's.price',
        'hotel': 'h.hotel_name'
    }
    sort_col = valid_sorts.get(sort_by, 's.service_name')
    sort_dir = 'DESC' if order == 'desc' else 'ASC'

    base_query = """
        SELECT 
            s.service_id,
            s.service_name,
            s.description,
            s.price,
            h.hotel_id,
            h.hotel_name,
            h.location,
            h.star_rating
        FROM SERVICE s
        INNER JOIN HOTEL h ON s.hotel_id = h.hotel_id
        WHERE 1=1
    """
    params = []

    if search:
        base_query += " AND (s.service_name LIKE %s OR s.description LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    if hotel_id and hotel_id.isdigit():
        base_query += " AND s.hotel_id = %s"
        params.append(int(hotel_id))

    base_query += f" ORDER BY {sort_col} {sort_dir}"

    services = query_all(base_query, tuple(params))
    hotels = query_all("SELECT hotel_id, hotel_name FROM HOTEL ORDER BY hotel_name ASC")

    return render_template(
        'services.html',
        services=services,
        hotels=hotels,
        filters={'search': search, 'hotel_id': hotel_id, 'sort_by': sort_by, 'order': order}
    )
