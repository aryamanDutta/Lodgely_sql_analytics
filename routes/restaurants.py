from flask import Blueprint, render_template, request
from db.connection import query_all

restaurants_bp = Blueprint('restaurants', __name__, url_prefix='/restaurants')

@restaurants_bp.route('/')
def list_restaurants_and_food():
    restaurant_id = request.args.get('restaurant_id', '').strip()
    cuisine_type = request.args.get('cuisine_type', '').strip()
    category = request.args.get('category', '').strip()
    availability = request.args.get('availability', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()

    base_query = """
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
        WHERE 1=1
    """
    params = []

    if restaurant_id and restaurant_id.isdigit():
        base_query += " AND r.restaurant_id = %s"
        params.append(int(restaurant_id))

    if cuisine_type:
        base_query += " AND r.cuisine_type LIKE %s"
        params.append(f"%{cuisine_type}%")

    if category:
        base_query += " AND f.category = %s"
        params.append(category)

    if availability:
        base_query += " AND f.availability = %s"
        params.append(availability)

    if min_price:
        try:
            base_query += " AND f.price >= %s"
            params.append(float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            base_query += " AND f.price <= %s"
            params.append(float(max_price))
        except ValueError:
            pass

    base_query += " ORDER BY r.restaurant_name, f.food_name ASC"

    menu_items = query_all(base_query, tuple(params))
    restaurants = query_all("SELECT restaurant_id, restaurant_name, cuisine_type FROM RESTAURANT ORDER BY restaurant_name ASC")
    categories = ['Appetizer', 'Main Course', 'Dessert', 'Beverage', 'Snacks']

    return render_template(
        'restaurants.html',
        menu_items=menu_items,
        restaurants=restaurants,
        categories=categories,
        filters={
            'restaurant_id': restaurant_id,
            'cuisine_type': cuisine_type,
            'category': category,
            'availability': availability,
            'min_price': min_price,
            'max_price': max_price
        }
    )
