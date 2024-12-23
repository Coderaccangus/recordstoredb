from init import db, ma

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    inventory_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.supplier_id'), nullable=False)
    record_id = db.Column(db.Integer, db.ForeignKey('records.record_id'), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
class InventorySchema(ma.Schema):
    class Meta:
        fields = ("inventory_id", "supplier_id","record_id", "stock_quantity", "price")

inventory_schema = InventorySchema()
inventory_schema_many = InventorySchema(many=True)
