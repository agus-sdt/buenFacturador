from flask import Flask,redirect,url_for,render_template,request
from flask_login import login_required, current_user
from config import Config
from extensions import db, login_manager
from sqlalchemy import text, func, extract
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)

from models.usuario import Usuario
from models.cliente import Cliente
from models.producto import Producto
from models.factura import Factura
from models.detalle_factura import DetalleFactura



@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


from routes.auth import auth_bp
from routes.clientes import clientes_bp
from routes.productos import productos_bp
from routes.facturas import facturas_bp
from routes.reportes import reportes_bp


app.register_blueprint(auth_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(facturas_bp)
app.register_blueprint(reportes_bp)



with app.app_context():
    db.create_all()
    print("Tablas creadas en MySQL")




@app.route('/testBD')
def testBD():
    try:
        db.session.execute(text("select 1"))
        return "conexion exitosa"
    except Exception as e:
        return f"fallo la conexion {e}"



@app.route('/')
@login_required
def dashboard():
    total_clientes = Cliente.query.count()
    total_productos = Producto.query.count()
    total_facturas = Factura.query.count()


    ahora = datetime.now()
    ventas_mes = db.session.query(func.sum(Factura.total)).filter(
        extract('month', Factura.fecha) == ahora.month,
        extract('year', Factura.fecha) == ahora.year
    ).scalar() or 0



    facturas_pagadas = Factura.query.filter_by(estado='pagada').all()
    total_ventas_mes = sum(float(f.total) for f in facturas_pagadas)

    ultimos_clientes = Cliente.query.order_by(Cliente.id_cliente.desc()).limit(5).all()

    return render_template('dashboard.html', total_clientes=total_clientes, total_productos=total_productos, total_facturas=total_facturas, total_ventas_mes=total_ventas_mes, ultimos_clientes=ultimos_clientes, ventas_mes=ventas_mes)



with app.app_context():
    try:
        db.create_all()
        
        print("Sistema iniciado correctamente")
        
    except Exception as e:
        print(f"Error en inicialización: {e}")



if __name__ == "__main__":
    app.run(debug=True)