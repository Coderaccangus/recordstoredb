import os
from flask import Flask
from init import db, ma

from models.orders import Orders
from models.customers import Customers
from models.suppliers import Suppliers
from models.records import Records
from models.inventory import Inventory

from controllers.cli_controller import db_commands
from controllers.customer_controller import customers_bp
from controllers.supplier_controller import suppliers_bp
from controllers.order_controller import orders_bp
from controllers.inventory_controller import inventory_bp
from controllers.records_controller import records_bp

def create_app():
    app = Flask(__name__)

    # App configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URI")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    # Register Blueprints
    app.register_blueprint(db_commands)
    app.register_blueprint(customers_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(records_bp)

    # Create tables in the app context
    with app.app_context():
        db.create_all()  # Ensure all models are loaded before creating tables

    return app
