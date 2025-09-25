from extensions import db
from sqlalchemy import DECIMAL

class Producto(db.Model):
    __tablename__ = "productos"

    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descripcion =db.Column(db.String(200), nullable=False)
    precio = db.Column(DECIMAL(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0)

    detalles = db.relationship("DetalleFactura", backref="producto_relacion", lazy=True)

    def __repr__(self):
        return f"<Producto {self.descripcion}"