from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Modelo para la tabla de segmentos
class Segment(db.Model):
    __tablename__ = 'segments'
    __table_args__ = {"schema": "superstore"}
    segment_id = db.Column(db.Integer, primary_key=True)
    segment_name = db.Column(db.String(100))

# Modelo para la tabla de clientes
class Customer(db.Model):
    __tablename__ = 'customers'
    __table_args__ = {"schema": "superstore"}
    customer_id = db.Column(db.String(50), primary_key=True)
    customer_name = db.Column(db.String(255))
    segment_id = db.Column(db.Integer, db.ForeignKey('segments.segment_id'))

# Modelo para la tabla de categorías
class Category(db.Model):
    __tablename__ = 'categories'
    __table_args__ = {"schema": "superstore"}
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100))

# Modelo para la tabla de subcategorías
class Subcategory(db.Model):
    __tablename__ = 'subcategories'
    __table_args__ = {"schema": "superstore"}
    subcategory_id = db.Column(db.Integer, primary_key=True)
    subcategory_name = db.Column(db.String(100))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'))

# Modelo para la tabla de productos
class Product(db.Model):
    __tablename__ = 'products'
    __table_args__ = {"schema": "superstore"}
    product_pk = db.Column(db.Integer, primary_key=True)
    product_code = db.Column(db.String(50))
    product_name = db.Column(db.String(255))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.subcategory_id'))

# Modelo para la tabla de ubicaciones
class Location(db.Model):
    __tablename__ = 'locations'
    __table_args__ = {"schema": "superstore"}
    location_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    region = db.Column(db.String(50))

# Modelo para la tabla de métodos de envío
class ShipMode(db.Model):
    __table_args__ = {"schema": "superstore"}
    __tablename__ = 'ship_modes'
    ship_mode_id = db.Column(db.Integer, primary_key=True)
    ship_mode_name = db.Column(db.String(100))

# Modelo para la tabla de órdenes (pedidos)
class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = {"schema": "superstore"}
    order_id = db.Column(db.String(50), primary_key=True)
    order_date = db.Column(db.Date)
    ship_date = db.Column(db.Date)
    customer_id = db.Column(db.String(50), db.ForeignKey('customers.customer_id'))
    ship_mode_id = db.Column(db.Integer, db.ForeignKey('ship_modes.ship_mode_id'))
    location_id = db.Column(db.Integer, db.ForeignKey('locations.location_id'))

# Modelo para los detalles de las órdenes
class OrderDetail(db.Model):
    __tablename__ = 'order_details'
    __table_args__ = {"schema": "superstore"}
    order_detail_id = db.Column(db.Integer, primary_key=True)
    row_id = db.Column(db.Integer)
    order_id = db.Column(db.String(50), db.ForeignKey('orders.order_id'))
    product_pk = db.Column(db.Integer, db.ForeignKey('products.product_pk'))
    sales = db.Column(db.Numeric(15, 4))
    quantity = db.Column(db.Integer)
    discount = db.Column(db.Numeric(5, 4))
    profit = db.Column(db.Numeric(15, 4))