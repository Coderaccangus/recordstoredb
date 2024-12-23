from flask import Blueprint, request  # type: ignore
from sqlalchemy.exc import IntegrityError  # type: ignore
from psycopg2 import errorcodes  # type: ignore
from init import db
from models.records import Records, records_schema, record_schema
from models.inventory import Inventory, inventory_schema, inventory_schema_many  # Ensure Inventory and InventoryShipments are imported

records_bp = Blueprint("records", __name__, url_prefix="/records")

# READ all - /records - GET
@records_bp.route("/")
def get_records():
    stmt = db.select(Records)
    record_list = db.session.scalars(stmt)
    data = records_schema.dump(record_list)
    return data

# Read one - /records/id - GET
@records_bp.route("/<int:record_id>")
def get_record(record_id):
    stmt = db.select(Records).filter_by(record_id=record_id)
    record = db.session.scalar(stmt)

    if record:
        # Serialize and return the record data
        data = record_schema.dump(record)
        return data
    else:
        # error message
        return {"message": f"Record with id {record_id} does not exist"}, 404

# Filter records by artist - /records/artist/<artist> - GET
@records_bp.route("/artist/<string:artist>")
def get_records_by_artist(artist):
    stmt = db.select(Records).filter(Records.artist.ilike(f"%{artist}%"))
    record_list = db.session.scalars(stmt)
    if record_list:
        data = records_schema.dump(record_list)
        return data
    else:
        return {"message": f"No records found for artist '{artist}'"}, 404

# Filter records by genre - /records/genre/<genre> - GET
@records_bp.route("/genre/<string:genre>")
def get_records_by_genre(genre):
    stmt = db.select(Records).filter(Records.genre.ilike(f"%{genre}%"))
    record_list = db.session.scalars(stmt)
    if record_list:
        data = records_schema.dump(record_list)
        return data
    else:
        return {"message": f"No records found for genre '{genre}'"}, 404

# CREATE - /records - POST
@records_bp.route("/", methods=["POST"])
def create_record():
    try:
        # Get the request data
        body_data = request.get_json()

        title = body_data.get("title")
        artist = body_data.get("artist")
        genre = body_data.get("genre")
        price = body_data.get("price")

        if not title or not artist or not genre:
            return {"message": "All fields are required."}, 400

        # Create the new record
        new_record = Records(
            title=title,
            artist=artist,
            genre=genre,
            price=price,
        )

        # Add to the session and commit
        db.session.add(new_record)
        db.session.commit()

        # Return the created record
        return record_schema.dump(new_record), 201

    except IntegrityError as err:
        if err.orig.pgcode == errorcodes.NOT_NULL_VIOLATION:
            return {"message": "A required field is missing."}, 400
        elif err.orig.pgcode == errorcodes.UNIQUE_VIOLATION:
            return {"message": "A record with this information already exists."}, 409
        else:
            return {"message": "An unexpected error occurred."}, 500

# DELETE - /records/<id> - DELETE
@records_bp.route("/<int:record_id>", methods=["DELETE"])
def delete_record(record_id):
    # Find the record to be deleted using id
    stmt = db.select(Records).filter_by(record_id=record_id)
    record = db.session.scalar(stmt)  # Fetch the record

    # If record exists, proceed to check for associated shipments
    if record:
        # Check if any inventory shipments are linked to this record
        shipments_stmt = db.select(Inventory).filter_by(record_id=record_id)
        shipments = db.session.scalars(shipments_stmt).all()

        # If there are associated shipments, return an error
        if shipments:
            return {"Message": f"Record with id '{record_id}' cannot be deleted because it has associated shipments."}, 400

        # Delete the record if no shipments are linked
        db.session.delete(record)
        db.session.commit()  # Commit the changes to the database

        # Return success response
        return {"Message": f"Record with id '{record_id}' deleted successfully."}, 200
    else:
        # Return error response if record does not exist
        return {"Message": f"Record with id '{record_id}' does not exist."}, 404
