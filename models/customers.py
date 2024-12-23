from init import db, ma

class Customers(db.Model):
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.Integer, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    
class CustomersSchema(ma.Schema):
    class Meta:
        fields = ("customer_id", "name", "email","phone_number","address")



customer_schema = CustomersSchema()  # For a single customer
customers_schema = CustomersSchema(many=True)  # For multiple customers
