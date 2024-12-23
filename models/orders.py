from init import db, ma

class Orders(db.Model):
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.customer_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('records.record_id'), nullable=False)
    order_date = db.Column(db.String(255), nullable=True)

class OrdersSchema(ma.Schema):
    class Meta:
        fields = ("order_id", "customer_id","record_id", "order_date")


order_schema = OrdersSchema()  # For a single order
orders_schema = OrdersSchema(many=True)  # For multiple orders
