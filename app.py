import os
import traceback
from flask import Flask, render_template, jsonify, request
from sqlalchemy import func, extract, inspect
from models import db, Customer, Segment, Order, Location, ShipMode, OrderDetail, Product, Subcategory, Category
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/detalle')
def detalle():
    return render_template('detalle.html')

# Función para envolver respuestas y capturar errores globales en JSON
def error_handler(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Imprime el error en la terminal para que puedas verlo
            print("ERROR EN EL SERVIDOR:")
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    wrapper.__name__ = f.__name__
    return wrapper

@app.route('/api/filters', methods=['GET'])
@error_handler
def get_filters():
    segments = db.session.query(Segment.segment_name).distinct().all()
    regions = db.session.query(Location.region).distinct().all()
    years = db.session.query(extract('year', Order.order_date).label('year')).distinct().order_by('year').all()
    categories = db.session.query(Category.category_name).distinct().all()
    
    return jsonify({
        'segments': [s[0] for s in segments if s[0]],
        'regions': [r[0] for r in regions if r[0]],
        'years': [int(y[0]) for y in years if y[0]],
        'categories': [c[0] for c in categories if c[0]]
    })

def apply_filters(query, segment, region, year, category):
    if segment:
        query = query.filter(Segment.segment_name == segment)
    if region:
        query = query.filter(Location.region == region)
    if year:
        query = query.filter(extract('year', Order.order_date) == int(year))
    if category:
        query = query.filter(Category.category_name == category)
    return query

@app.route('/api/kpis', methods=['GET'])
@error_handler
def get_kpis():
    segment = request.args.get('segment')
    region = request.args.get('region')
    year = request.args.get('year')
    category = request.args.get('category')

    base_query = db.session.query(
        Order.customer_id,
        Order.order_id,
        OrderDetail.sales
    ).join(Customer, Order.customer_id == Customer.customer_id) \
     .join(Segment, Customer.segment_id == Segment.segment_id) \
     .join(Location, Order.location_id == Location.location_id) \
     .join(OrderDetail, Order.order_id == OrderDetail.order_id) \
     .join(Product, OrderDetail.product_pk == Product.product_pk) \
     .join(Subcategory, Product.subcategory_id == Subcategory.subcategory_id) \
     .join(Category, Subcategory.category_id == Category.category_id)

    base_query = apply_filters(base_query, segment, region, year, category)
    subq = base_query.subquery()

    total_clientes = db.session.query(func.count(func.distinct(subq.c.customer_id))).scalar() or 0
    clientes_activos = total_clientes 
    total_sales = db.session.query(func.sum(subq.c.sales)).scalar() or 0
    total_orders = db.session.query(func.count(func.distinct(subq.c.order_id))).scalar() or 1
    
    ticket_promedio = float(total_sales) / total_orders if total_orders > 0 else 0
    ventas_promedio_cliente = float(total_sales) / total_clientes if total_clientes > 0 else 0

    return jsonify({
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'ticket_promedio': round(ticket_promedio, 2),
        'ventas_promedio_cliente': round(ventas_promedio_cliente, 2)
    })

@app.route('/api/charts', methods=['GET'])
@error_handler
def get_charts():
    segment = request.args.get('segment')
    region = request.args.get('region')
    year = request.args.get('year')
    category = request.args.get('category')

    base_query = db.session.query(
        Segment.segment_name,
        Customer.customer_name,
        Location.region,
        Order.order_id,
        OrderDetail.sales
    ).join(Order, Order.order_id == OrderDetail.order_id) \
     .join(Customer, Order.customer_id == Customer.customer_id) \
     .join(Segment, Customer.segment_id == Segment.segment_id) \
     .join(Location, Order.location_id == Location.location_id) \
     .join(Product, OrderDetail.product_pk == Product.product_pk) \
     .join(Subcategory, Product.subcategory_id == Subcategory.subcategory_id) \
     .join(Category, Subcategory.category_id == Category.category_id)

    filtered_query = apply_filters(base_query, segment, region, year, category)
    subq = filtered_query.subquery()

    ventas_segmento = db.session.query(
        subq.c.segment_name, func.sum(subq.c.sales).label('total_sales')
    ).group_by(subq.c.segment_name).all()

    top_clientes = db.session.query(
        subq.c.customer_name, func.sum(subq.c.sales).label('total_sales')
    ).group_by(subq.c.customer_name).order_by(func.sum(subq.c.sales).desc()).limit(10).all()

    clientes_region = db.session.query(
        subq.c.region, func.count(func.distinct(subq.c.customer_name)).label('total_customers')
    ).group_by(subq.c.region).all()

    ticket_segmento = db.session.query(
        subq.c.segment_name,
        (func.sum(subq.c.sales) / func.count(func.distinct(subq.c.order_id))).label('ticket_promedio')
    ).group_by(subq.c.segment_name).all()

    return jsonify({
        'ventas_segmento': [{'label': row[0], 'value': float(row[1])} for row in ventas_segmento if row[1] is not None],
        'top_clientes': [{'label': row[0], 'value': float(row[1])} for row in top_clientes if row[1] is not None],
        'clientes_region': [{'label': row[0], 'value': int(row[1])} for row in clientes_region if row[1] is not None],
        'ticket_segmento': [{'label': row[0], 'value': float(row[1])} for row in ticket_segmento if row[1] is not None]
    })

@app.route('/api/table_data', methods=['GET'])
@error_handler
def get_table_data():
    segment = request.args.get('segment')
    region = request.args.get('region')
    year = request.args.get('year')
    category = request.args.get('category')

    base_query = db.session.query(
        Customer.customer_name,
        Segment.segment_name,
        Location.region,
        Order.order_id,
        OrderDetail.sales,
        OrderDetail.profit
    ).join(Order, Order.customer_id == Customer.customer_id) \
     .join(Segment, Customer.segment_id == Segment.segment_id) \
     .join(Location, Order.location_id == Location.location_id) \
     .join(OrderDetail, Order.order_id == OrderDetail.order_id) \
     .join(Product, OrderDetail.product_pk == Product.product_pk) \
     .join(Subcategory, Product.subcategory_id == Subcategory.subcategory_id) \
     .join(Category, Subcategory.category_id == Category.category_id)

    filtered_query = apply_filters(base_query, segment, region, year, category)
    subq = filtered_query.subquery()

    ranking = db.session.query(
        subq.c.customer_name,
        subq.c.segment_name,
        subq.c.region,
        func.count(func.distinct(subq.c.order_id)).label('total_pedidos'),
        func.sum(subq.c.sales).label('total_ventas'),
        func.sum(subq.c.profit).label('total_ganancia')
    ).group_by(
        subq.c.customer_name,
        subq.c.segment_name,
        subq.c.region
    ).order_by(func.sum(subq.c.sales).desc()).all()

    data = []
    for row in ranking:
        total_pedidos = int(row[3])
        total_ventas = float(row[4] or 0)
        total_ganancia = float(row[5] or 0)
        ticket_promedio = total_ventas / total_pedidos if total_pedidos > 0 else 0
        
        data.append({
            'cliente': row[0],
            'segmento': row[1],
            'region': row[2],
            'total_pedidos': total_pedidos,
            'total_ventas': round(total_ventas, 2),
            'total_ganancia': round(total_ganancia, 2),
            'ticket_promedio': round(ticket_promedio, 2)
        })

    return jsonify(data)

@app.route('/api/database_tables', methods=['GET'])
@error_handler
def get_database_tables():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return jsonify({'tables': tables})

@app.route('/api/database_data', methods=['GET'])
@error_handler
def get_database_data():
    table_name = request.args.get('table')
    limit = request.args.get('limit', 100, type=int)
    
    if not table_name:
        return jsonify({'error': 'No table provided'}), 400

    inspector = inspect(db.engine)
    if table_name not in inspector.get_table_names():
        return jsonify({'error': 'Table not found'}), 404

    from sqlalchemy import text
    query = text(f"SELECT * FROM {table_name} LIMIT :limit")
    result = db.session.execute(query, {'limit': limit})
    
    columns = result.keys()
    data = [dict(zip(columns, row)) for row in result.fetchall()]
    
    return jsonify({
        'columns': list(columns),
        'data': data
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)