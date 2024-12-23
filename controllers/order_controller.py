from flask import Blueprint, request # type: ignore
from sqlalchemy.exc import IntegrityError # type: ignore
from psycopg2 import errorcodes # type: ignore
from init import db
from models.orders import Orders, orders_schema, order_schema
from models.customers import Customers

from models.orders import Orders
from models.customers import Customers



orders_bp= Blueprint("orders", __name__, url_prefix="/orders")

# READ all - /orders - GET
@orders_bp.route("/")
def get_orders():
    stmt = db.select(Orders)
    orders_list = db.session.scalars(stmt)
    data = orders_schema.dump(orders_list)
    return data

# Read one - /orders/id - GET
@orders_bp.route("/<int:order_id>")
def get_order(order_id):
    # Correct filter to match the primary key in Orders
    stmt = db.select(Orders).filter_by(order_id=order_id)
    order = db.session.scalar(stmt)

    if order:
        # Serialize and return the order data
        data = order_schema.dump(order)
        return data
    else:
        # Correct the error message
        return {"message": f"Order with id {order_id} does not exist"}, 404


# Filter orders by customer_id - /orders/filter_by_customer_id?customer_id=<customer_id> - GET
@orders_bp.route("/filter_by_customer_id")
def get_orders_by_customer_id():
    customer_id = request.args.get("customer_id", type=int)
    
    if not customer_id:
        return {"message": "Customer ID is required."}, 400
    
    # Check if the customer exists
    customer = db.session.get(Customers, customer_id)
    if not customer:
        return {"message": f"No customer found with id {customer_id}"}, 404
    
    # If the customer exists, fetch their orders
    stmt = db.select(Orders).filter_by(customer_id=customer_id)
    orders_list = db.session.scalars(stmt)
    
    if orders_list:
        data = orders_schema.dump(orders_list)  # Serialize the list of orders
        return data
    else:
        return {"message": f"No orders found for customer with id {customer_id}"}, 404




# CREATE - /order - POST
@orders_bp.route("/", methods=["POST"])
def create_order():
    try:
        # get information from the request body
        body_data = request.get_json()
        #Create customer instance
        new_order = Orders(
            customer_id=body_data.get("customer_id"),
            record_id=body_data.get("record_id"),
            order_date=body_data.get("order_date"),
        )
        # add to the session 
        db.session.add(new_order)
        # commit
        db.session.commit()
        # return a responce
        return order_schema.dump(new_order), 201
    except IntegrityError as err:
        print(err.orig.pgcode)
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            # not null violation
            return {"Message":f"The field {err.orig.diag.column_name} is required"}, 409

# Delete - /orders/id - DELETE
@orders_bp.route("/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    # Find the order to be deleted using id
    stmt = db.select(Orders).filter_by(order_id=order_id)
    order = db.session.scalar(stmt)

    # If the order exists
    if order:
        # Check if the order has a customer linked to it
        if order.customer_id:
            return {"Message": f"Cannot delete order with id '{order_id}' because it is linked to a customer."}, 400
        
        # Delete the order if not linked to a customer
        db.session.delete(order)
        db.session.commit()
        return {"Message": f"Order '{order_id}' deleted successfully"}

    # Else, return error if the order does not exist
    else:
        return {"Message": f"Order with id '{order_id}' does not exist"}, 404
    
# Update - /orders/id - PUT, PATCH
@orders_bp.route("/<int:order_id>", methods=["PUT","PATCH"])
def update_order(order_id):  
      
        # find the order to be updated
        stmt = db.select(Orders).filter_by(order_id=order_id)
        orders = db.session.scalar(stmt)
        #get the data to be updated 
        body_data = request.get_json()
        #if customer exists
        if orders:
            # update the customer data
            orders.order_date = body_data.get("order_date") or orders.order_date
            orders.total_amount = body_data.get("total_amount") or orders.order.total_amount
            # commit changes
            db.session.commit()
            # return updated data
            return order_schema.dump(orders)
        #else
        else:
            #return error message
            return {"Message" : f"customer with id {order_id} does not exits"},404

