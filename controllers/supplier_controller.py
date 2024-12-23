from flask import Blueprint, request  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from psycopg2 import errorcodes  # type: ignore
from init import db
from models.suppliers import Suppliers, supplier_schema, suppliers_schema
from models.inventory import Inventory

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")

# READ all - /suppliers - GET
@suppliers_bp.route("/", methods=["GET"])
def get_suppliers():
    stmt = db.select(Suppliers)
    suppliers_list = db.session.scalars(stmt)
    data = suppliers_schema.dump(suppliers_list)
    return data

# READ one - /suppliers/<id> - GET
@suppliers_bp.route("/<int:supplier_id>", methods=["GET"])
def get_supplier(supplier_id):
    stmt = db.select(Suppliers).filter_by(supplier_id=supplier_id)
    supplier = db.session.scalar(stmt)
    if supplier:
        data = supplier_schema.dump(supplier)
        return data
    else:
        return {"message": f"Supplier with id {supplier_id} does not exist"}, 404

# CREATE - /suppliers - POST
@suppliers_bp.route("/", methods=["POST"])
def create_supplier():
    try:
        # Get information from the request body
        body_data = request.get_json()
        
        # Create a new supplier instance
        new_supplier = Suppliers(
            name=body_data.get("name"),
            email=body_data.get("email"),
            phone_number=body_data.get("phone_number")
        )
        
        # Add to the session
        db.session.add(new_supplier)
        
        # Commit
        db.session.commit()
        
        # Return the response with the created supplier
        return supplier_schema.dump(new_supplier), 201
    except IntegrityError as err:
        print(err.orig.pgcode)
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            # Not null violation
            return {"Message": f"The field {err.orig.diag.column_name} is required"}, 409
        
        if err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            # Unique constraint violation
            return {"Message": "Email or Phone number already in use"}, 409

# DELETE - /suppliers/<id> - DELETE
@suppliers_bp.route("/<int:supplier_id>", methods=["DELETE"])
def delete_supplier(supplier_id):
    # Find the supplier to be deleted using supplier_id
    stmt = db.select(Suppliers).filter_by(supplier_id=supplier_id)  # Use supplier_id here
    supplier = db.session.scalar(stmt)

    # If the supplier exists
    if supplier:
        # Fetch and delete all associated inventory items
        stmt = db.select(Inventory).filter_by(supplier_id=supplier_id)
        inventory_items = db.session.scalars(stmt)
        
        # Delete associated inventory items
        for item in inventory_items:
            db.session.delete(item)

        # Delete the supplier
        db.session.delete(supplier)
        db.session.commit()

        # Return success message
        return {"Message": f"Supplier '{supplier.name}' and associated inventory items deleted successfully"}, 200

    # If the supplier doesn't exist
    else:
        return {"Message": f"Supplier with id '{supplier_id}' does not exist"}, 404

# UPDATE - /suppliers/<id> - PUT, PATCH
@suppliers_bp.route("/<int:supplier_id>", methods=["PUT", "PATCH"])
def update_supplier(supplier_id):  
    try:  
        # Find the supplier to be updated
        stmt = db.select(Suppliers).filter_by(supplier_id=supplier_id)  # Use supplier_id here
        supplier = db.session.scalar(stmt)
        
        # Get the data to be updated 
        body_data = request.get_json()
        
        # If supplier exists
        if supplier:
            # Update the supplier fields if provided
            supplier.name = body_data.get("name") or supplier.name
            supplier.email = body_data.get("contact_email") or supplier.email
            supplier.phone_number = body_data.get("phone_number") or supplier.phone_number 
            
            # Commit the changes to the database
            db.session.commit()
            
            # Return the updated supplier data
            return supplier_schema.dump(supplier)
        else:
            return {"Message": f"Supplier with id {supplier_id} does not exist"}, 404
        
    except IntegrityError:
        return {"Message": "Email or Phone number already in use"}, 409
