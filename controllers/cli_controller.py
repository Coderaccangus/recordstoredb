from flask import Blueprint  # type: ignore
from flask import Flask # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore
from init import db
from models.orders import Orders
from models.customers import Customers
from models.suppliers import Suppliers
from models.records import Records
from models.inventory import Inventory
from datetime import datetime

db_commands = Blueprint("db", __name__)

@db_commands.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created")

@db_commands.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")

@db_commands.cli.command("seed")
def seed_all_data():
    # Create some sample customers
    customers = [
        Customers(name="customer1", email="customer1@email.com", phone_number="0412345678", address="201 smith st"),
        Customers(name="customer2", email="customer2@email.com", phone_number="0488888888", address="555 Lygon st")
    ]
    db.session.add_all(customers)

    print("Customers seeded")

    # Create some sample suppliers
    suppliers = [
        Suppliers(name="Supplier1", email="Supplier1@email.com", phone_number="0477777777"),
        Suppliers(name="Supplier2", email="Supplier2@email.com", phone_number="0466666666")
    ]
    db.session.add_all(suppliers)

    # Commit changes for customers and suppliers
    db.session.commit()
    print("Suppliers seeded")

    # Create sample records
    records = [
        Records(title="Joey's Mixtape", artist="Joey Smalls", genre="hiphop", price=15.00),
        Records(title="TOP 40 NOW", artist="Various Artists", genre="pop", price=11.00),
        Records(title="Birdshop", artist="Birdparty", genre="Indie", price=18.00)
    ]
    db.session.add_all(records)
    db.session.commit()
    print("Records seeded")

    # Create orders with proper date formatting
    orders = [
        Orders(customer_id=1, record_id=1, order_date="09/06/22"),
        Orders(customer_id=2, record_id=2, order_date="04/04/23")
    ]
    db.session.add_all(orders)
    db.session.commit()
    print("Orders seeded")

    # Create inventory records
    shipments = [
        Inventory(supplier_id=1, record_id=1, stock_quantity=500, price=50),
        Inventory(supplier_id=2, record_id=2, stock_quantity=20, price=30)
    ]
    db.session.add_all(shipments)
    db.session.commit()
    print("Inventory seeded")
