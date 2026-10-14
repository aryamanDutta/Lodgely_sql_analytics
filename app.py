import logging
import os
import time
from flask import Flask, render_template, jsonify
from config import Config
from db.connection import check_db_connection, init_db_from_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    from routes.dashboard import dashboard_bp
    from routes.rooms import rooms_bp
    from routes.customers import customers_bp
    from routes.bookings import bookings_bp
    from routes.payments import payments_bp
    from routes.restaurants import restaurants_bp
    from routes.services import services_bp
    from routes.employees import employees_bp
    from routes.housekeeping import housekeeping_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(rooms_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(payments_bp)
    app.register_blueprint(restaurants_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(housekeeping_bp)
    app.register_blueprint(analytics_bp)

    # Context processor for global template variables
    @app.context_processor
    def inject_globals():
        return {
            'app_title': 'Grand Luxe Hotel ERP System',
            'academic_project': 'CAM 5 Database Application',
            'current_year': 2026
        }

    # Health check endpoint
    @app.route('/health')
    def health():
        db_ok = check_db_connection()
        status_code = 200 if db_ok else 503
        return jsonify({
            'status': 'healthy' if db_ok else 'unhealthy',
            'database_connected': db_ok,
            'host': Config.DB_HOST,
            'database': Config.DB_NAME
        }), status_code

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error("Internal Server Error: %s", str(e))
        return render_template('errors/500.html', error="An unexpected server error occurred."), 500

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        logger.error("Unhandled Exception caught: %s", str(e), exc_info=True)
        # Check if it's a database connection issue
        err_str = str(e).lower()
        if 'connection' in err_str or 'access denied' in err_str or 'unknown database' in err_str or 'operationalerror' in err_str:
            return render_template('errors/500.html', error="Database connection error. Please ensure the MySQL database service is running and accessible."), 500
        return render_template('errors/500.html', error="An error occurred while processing your request."), 500

    return app

def wait_for_db_and_initialize(max_retries=15, delay=2):
    """Wait for MySQL database readiness and execute schema if not initialized."""
    logger.info("Attempting to connect to MySQL database at %s:%s...", Config.DB_HOST, Config.DB_PORT)
    sql_path = os.path.join(os.path.dirname(__file__), 'database', 'init.sql')

    for attempt in range(1, max_retries + 1):
        if check_db_connection():
            logger.info("MySQL connection established successfully.")
            return True
        logger.warning("Database not ready yet (attempt %d/%d). Retrying in %d seconds...", attempt, max_retries, delay)
        time.sleep(delay)

    logger.warning("Could not connect to MySQL after %d attempts. Attempting multi-statement init...", max_retries)
    try:
        if os.path.exists(sql_path):
            init_db_from_file(sql_path)
            logger.info("Database initialized from init.sql.")
            return True
    except Exception as e:
        logger.error("Failed to auto-initialize database: %s", str(e))
    return False

app = create_app()

if __name__ == '__main__':
    # When executed directly, wait for DB readiness if running against live DB
    wait_for_db_and_initialize(max_retries=5, delay=1)
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
