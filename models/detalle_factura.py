from extensions import db
from sqlalchemy import DECIMAL
from decimal import Decimal

class DetalleFactura(db.Model):
    __tablename__ = "detalle_factura"

    id_detalle = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_factura = db.Column(db.Integer, db.ForeignKey("facturas.id_factura"), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey("productos.id_producto"), nullable=False)
    
    descripcion_producto = db.Column(db.String(200), nullable=False)
    precio_unitario = db.Column(DECIMAL(10, 2), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(DECIMAL(10, 2), nullable=False)

    producto = db.relationship('Producto', backref=db.backref('detalle_factura', lazy=True))

    def __repr__(self):
        return f"<DetalleFactura {self.descripcion_producto} x {self.cantidad}>"

def calcular_subtotal(self):
        """calcula el subtotal de esta linea"""
        self.subtotal = Decimal(str(self.precio_unitario)) * Decimal(str(self.cantidad))