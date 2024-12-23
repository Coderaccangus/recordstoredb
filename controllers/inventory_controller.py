from flask import Blueprint, request  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from psycopg2 import errorcodes  # type: ignore
from init import db
from models.inventory import Inventory, inventory_schema, inventory_schema_many
from models.suppliers import Suppliers
from models.records import Records

# Define the blueprint for the inventory
inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

# READ all - /inventory - GET
@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    stmt = db.select(Inventory)
    inventory_list = db.session.scalars(stmt)
    data = inventory_schema_many.dump(inventory_list)
    return data

# READ one - /inventory/<id> - GET
@inventory_bp.route("/<int:inventory_id>", methods=["GET"])
def get_inventory_item(inventory_id):
    # Correct filter to match the primary key in inventory
    stmt = db.select(Inventory).filter_by(inventory_id=inventory_id)
    inventory_item = db.session.scalar(stmt)

    if inventory_item:
        # Serialize and return the inventory data
        data = inventory_schema.dump(inventory_item)
        return data
    else:
        # error message if inventory item not found
        return {"message": f"Inventory item with id {inventory_id} does not exist"}, 404

# Filter inventory by supplier_id - /inventory/filter_by_supplier_id?supplier_id=<supplier_id> - GET
@inventory_bp.route("/filter_by_supplier_id", methods=["GET"])
def get_inventory_by_supplier_id():
    supplier_id = request.args.get("supplier_id", type=int)
    
    if not supplier_id:
        return {"message": "Supplier ID is required."}, 400  
    
    # Check if the supplier exists
    supplier = db.session.get(Suppliers, supplier_id)
    if not supplier:
        return {"message": f"No supplier found with id {supplier_id}"}, 404  
    
    # Fetch the inventory items for the given supplier
    stmt = db.select(Inventory).filter_by(supplier_id=supplier_id)
    inventory_list = db.session.scalars(stmt)
    
    if inventory_list:
        data = inventory_schema_many.dump(inventory_list)
        return data  
    else:
        return {"message": f"No inventory items found for supplier with id {supplier_id}"}, 404 

# CREATE - /inventory - POST
@inventory_bp.route("/", methods=["POST"])
def create_inventory_item():
    try:
        # Get the request data
        body_data = request.get_json()

        # Ensure the required fields are present
        supplier_id = body_data.get("supplier_id")
        record_id = body_data.get("record_id")
        price = body_data.get("price")
        stock_quantity = body_data.get("stock_quantity")

        if not all([supplier_id, record_id]):
            return {"message": "All fields are required."}, 400

        # Check if the record exists
        record = db.session.get(Records, record_id)
        if not record:
            return {"message": f"No record found with id {record_id}"}, 404

        # Check if the supplier exists
        supplier = db.session.get(Suppliers, supplier_id)
        if not supplier:
            return {"message": f"No supplier found with id {supplier_id}"}, 404

        # Create a new Inventory item
        new_inventory_item = Inventory(
            record_id=record_id,
            supplier_id=supplier_id,
            price=price,
            stock_quantity = stock_quantity
        )

        # Add to the session and commit
        db.session.add(new_inventory_item)
        db.session.commit()

        # Return the created inventory item
        return inventory_schema.dump(new_inventory_item), 201

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"message": "A required field is missing."}, 400
        else:
            return {"message": "An unexpected error occurred."}, 500

# DELETE - /inventory/id - DELETE
@inventory_bp.route("/<int:inventory_id>", methods=["DELETE"])
def delete_inventory_item(inventory_id):
    # Find the inventory item to be deleted using inventory_id
    stmt = db.select(Inventory).filter_by(inventory_id=inventory_id)
    inventory_item = db.session.scalar(stmt)

    # If the inventory item exists
    if inventory_item:
        # Delete the inventory item
        db.session.delete(inventory_item)
        db.session.commit()
        return {"Message": f"Inventory item '{inventory_id}' deleted successfully"}, 200

    # If the inventory item doesn't exist
    else:
        return {"Message": f"Inventory item with id '{inventory_id}' does not exist"}, 404

# UPDATE - /inventory/id - PATCH
@inventory_bp.route("/<int:inventory_id>", methods=["PATCH"])
def update_inventory_item(inventory_id):
    try:
        # Get the request data
        body_data = request.get_json()

        # Find the existing inventory item
        inventory_item = Inventory.query.get(inventory_id)

        if not inventory_item:
            return {"message": f"Inventory item with id {inventory_id} not found."}, 404

        # Update the fields if they are provided
        if "quantity" in body_data:
            inventory_item.quantity = body_data["quantity"]
        if "price" in body_data:
            inventory_item.price = body_data["price"]
        if "shipment_date" in body_data:
            inventory_item.shipment_date = body_data["shipment_date"]
        if "added_date" in body_data:
            inventory_item.added_date = body_data["added_date"]
        if "supplier_id" in body_data:
            inventory_item.supplier_id = body_data["supplier_id"]

        # Commit the changes to the database
        db.session.commit()

        # Return the updated inventory item
        return inventory_schema.dump(inventory_item), 200

    except Exception as e:
        return {"message": f"An error occurred: {str(e)}"}, 500
