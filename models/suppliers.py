from init import db, ma

class Suppliers(db.Model):
    __tablename__ = 'suppliers'
    
    supplier_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)

class SuppliersSchema(ma.Schema):
    class Meta:
        fields = ("supplier_id", "name", "email", "phone_number")

supplier_schema = SuppliersSchema() 
suppliers_schema = SuppliersSchema(many=True)  