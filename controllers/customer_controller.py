from flask import Blueprint, request  # type: ignore
from sqlalchemy.exc import IntegrityError # type: ignore
from psycopg2 import errorcodes  # type: ignore
from init import db
from models.customers import Customers, customers_schema, customer_schema


customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

# READ all - /customers - GET
@customers_bp.route("/")
def get_customers():
    stmt = db.select(Customers)
    customers_list = db.session.scalars(stmt)
    data = customers_schema.dump(customers_list)
    return data

# Read one - /customers/id - GET
@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    stmt = db.select(Customers).filter_by(customer_id = customer_id)
    customer = db.session.scalar(stmt)
    
    if customer:
        data = customer_schema.dump(customer)
        return data
    else:
        return {"message": f"customer with id {customer_id} does not exist"}, 404


# CREATE - /customers - POST
@customers_bp.route("/", methods=["POST"])
def create_customer():
    try:
        # get information from the request body
        body_data = request.get_json()
        #Create customer instance
        new_customer = Customers(
            name=body_data.get("name"),
            email=body_data.get("email"),
            address=body_data.get("address"),
            phone_number=body_data.get("phone_number")
        )
        # add to the session 
        db.session.add(new_customer)
        # commit
        db.session.commit()
        # return a responce
        return customer_schema.dump(new_customer), 201
    except IntegrityError as err:
        print(err.orig.pgcode)
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            # not null violation
            return {"Message":f"The field {err.orig.diag.column_name} is required"}, 409
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # unique constant violation
            return {"Message":"Email or Phone number already in use"}, 409

# Delete - /customers/id - DELETE
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    # Find the customer to be deleted using the id
    stmt = db.select(Customers).filter_by(customer_id=customer_id)
    customer = db.session.scalar(stmt)
    
    # If the customer exists
    if customer:
        # Delete the customer (this will automatically delete their orders due to cascade)
        db.session.delete(customer)
        db.session.commit()

        # Return a response with a confirmation message
        return {"Message": f"Customer '{customer.name}' and their associated orders were deleted successfully."}

    # Else, return an error response if the customer does not exist
    else:
        return {"Message": f"Customer with id '{customer_id}' does not exist."}, 404


# Update - /customers/id - PUT, PATCH
@customers_bp.route("/<int:customer_id>", methods=["PUT","PATCH"])
def update_customer(customer_id):  
    try:  
        # find the customer to be updated
        stmt = db.select(Customers).filter_by(customer_id=customer_id)
        customer = db.session.scalar(stmt)
        #get the data to be updated 
        body_data = request.get_json()
        #if customer exists
        if customer:
            # update the customer data
            customer.name = body_data.get("name") or customer.name
            customer.email = body_data.get("email") or customer.email
            customer.address = body_data.get("address") or customer.address
            customer.phone_number = body_data.get("phone_number") or customer.phone_number 
            # commit changes
            db.session.commit()
            # return updated data
            return customer_schema.dump(customer)
        #else
        else:
            #return error message
            return {"Message" : f"customer with id {customer_id} does not exits"},404
        
    except IntegrityError:
        return {"Message":"Email or Phone number already in use"}, 409     
