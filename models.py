from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db = SQLAlchemy()


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    address = db.Column(db.String(200))


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))


class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    email = db.Column(db.String(120))
    address = db.Column(db.String(200))


class RawMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    quantity = db.Column(db.Float, default=0)
    unit = db.Column(db.String(20))
    minimum_stock = db.Column(db.Float, default=0)

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))

    supplier = db.relationship('Supplier', backref='raw_materials')
class BOMItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('product.id'),
        nullable=False
    )

    raw_material_id = db.Column(
        db.Integer,
        db.ForeignKey('raw_material.id'),
        nullable=False
    )

    quantity_required = db.Column(db.Float, nullable=False)

    product = db.relationship('Product', backref='bom_items')
    raw_material = db.relationship('RawMaterial', backref='bom_items')
class StockTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    raw_material_id = db.Column(
        db.Integer,
        db.ForeignKey('raw_material.id'),
        nullable=False
    )

    transaction_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200))

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    raw_material = db.relationship(
        'RawMaterial',
        backref='stock_transactions'
    )
class ProductionBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('product.id'),
        nullable=False
    )

    quantity = db.Column(db.Float, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    product = db.relationship(
        'Product',
        backref='production_batches'
    )  
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)