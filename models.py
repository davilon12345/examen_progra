from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customers'
    # Mapeo exacto de la tabla 'customers'
    customer_id = db.Column(db.String, primary_key=True)
    customer_name = db.Column(db.String)
    segment = db.Column(db.String)  # Si en la DB es segment_id, cámbialo aquí
    region = db.Column(db.String)

class Order(db.Model):
    __tablename__ = 'orders'
    # Mapeo exacto de la tabla 'orders'
    order_id = db.Column(db.String, primary_key=True)
    customer_id = db.Column(db.String, db.ForeignKey('customers.customer_id'))
    sales = db.Column(db.Float)
    profit = db.Column(db.Float)
    discount = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    order_date = db.Column(db.Date)