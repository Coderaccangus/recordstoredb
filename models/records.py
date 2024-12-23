from init import db, ma

class Records(db.Model):
    __tablename__ = 'records'
    
    record_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    genre = db.Column(db.String(255), nullable=True)
    
class RecordsSchema(ma.Schema):
    class Meta:
        fields = ("record_id", "title", "artist", "price", "genre")


record_schema = RecordsSchema()  # For a single record
records_schema = RecordsSchema(many=True)  # For multiple records
