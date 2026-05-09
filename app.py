from flask import Flask, render_template, jsonify, request
from models import db, Customer, Order
from sqlalchemy import func

app = Flask(__name__)

# Configuración de conexión (Asegúrate de usar tus credenciales)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Davilon_123@localhost:5432/Store2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    # Preparamos los filtros para evitar errores en el HTML
    segmentos = db.session.query(Customer.segment).distinct().all()
    regiones = db.session.query(Customer.region).distinct().all()
    
    filters = {
        'segments': [s[0] for s in segmentos if s[0]],
        'regions': [r[0] for r in regiones if r[0]]
    }
    return render_template('index.html', filters=filters)

@app.route('/api/data')
def get_data():
    segmento = request.args.get('segmento', 'all')
    query = Customer.query
    
    if segmento != 'all':
        query = query.filter(Customer.segment == segmento)
    
    clientes_lista = query.limit(10).all() # Limitamos a 10 para la tabla
    
    # ... tus cálculos de KPIs aquí ...

    return jsonify({
        'total_clientes': total_clientes,
        'clientes_activos': clientes_activos,
        'ticket_promedio': round(ticket_promedio, 2),
        'ventas_promedio_cliente': round(ventas_prom_cliente, 2),
        'clientes': [{
            'customer_id': c.customer_id,
            'customer_name': c.customer_name,
            'segment': c.segment,
            'region': c.region
        } for c in clientes_lista]
    })

if __name__ == '__main__':
    app.run(debug=True)