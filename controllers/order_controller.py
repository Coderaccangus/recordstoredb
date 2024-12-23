from flask import Blueprint, request  # Simplify imports
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from psycopg2 import errorcodes
from init import db
from models.orders import Orders
from models.records import Records
from models.customers import Customers
from models.orders import order_schema, orders_schema  # Import orders schema

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

# READ all - /orders - GET
@orders_bp.route("/")
def get_orders():
    stmt = db.select(Orders)
    orders_list = db.session.scalars(stmt)
    data = orders_schema.dump(orders_list)
    return data

# READ one - /orders/id - GET
@orders_bp.route("/<int:order_id>")
def get_order(order_id):
    stmt = db.select(Orders).filter_by(order_id=order_id)
    order = db.session.scalar(stmt)

    if order:
        return order_schema.dump(order)
    else:
        return {"message": f"Order with id {order_id} does not exist"}, 404

# Filter orders by customer_id - /orders/filter_by_customer_id - GET
@orders_bp.route("/filter_by_customer_id")
def get_orders_by_customer_id():
    customer_id = request.args.get("customer_id", type=int)
    
    if not customer_id:
        return {"message": "Customer ID is required."}, 400
    
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return {"message": f"No customer found with id {customer_id}"}, 404
    
    stmt = db.select(Orders).filter_by(customer_id=customer_id)
    orders_list = db.session.scalars(stmt)

    if orders_list:
        return orders_schema.dump(orders_list)
    else:
        return {"message": f"No orders found for customer with id {customer_id}"}, 404

# CREATE - /orders - POST
@orders_bp.route("/", methods=["POST"])
def create_order():
    try:
        body_data = request.get_json()

        record_id = body_data.get("record_id")
        if not record_id:
            return {"message": "Record ID is required to create an order."}, 400

        record = db.session.get(Records, record_id)
        if not record:
            return {"message": f"Record with ID {record_id} does not exist."}, 404

        new_order = Orders(
            customer_id=body_data.get("customer_id"),
            record_id=record_id,
            order_date=body_data.get("order_date"),
        )

        db.session.add(new_order)
        db.session.commit()
        return order_schema.dump(new_order), 201

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"message": f"The field {err.orig.diag.column_name} is required"}, 409
        return {"message": "An error occurred while creating the order."}, 500

# DELETE - /orders/id - DELETE
@orders_bp.route("/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    stmt = db.select(Orders).filter_by(order_id=order_id)
    order = db.session.scalar(stmt)

    if order:
        if order.customer_id:
            return {"message": f"Cannot delete order with id '{order_id}' because it is linked to a customer."}, 400
        
        db.session.delete(order)
        db.session.commit()
        return {"message": f"Order '{order_id}' deleted successfully"}

    else:
        return {"message": f"Order with id '{order_id}' does not exist"}, 404

# UPDATE - /orders/id - PUT, PATCH
@orders_bp.route("/<int:order_id>", methods=["PUT", "PATCH"])
def update_order(order_id):
    stmt = db.select(Orders).filter_by(order_id=order_id)
    order = db.session.scalar(stmt)
    body_data = request.get_json()

    if order:
        order.order_date = body_data.get("order_date", order.order_date)
        
        db.session.commit()
        return order_schema.dump(order)
    else:
        return {"message": f"Order with id {order_id} does not exist"}, 404
