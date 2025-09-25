from extensions import db
from sqlalchemy import DECIMAL
from datetime import datetime, timezone
from decimal import Decimal

class Factura(db.Model):
    __tablename__ = "facturas"

    id_factura = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    fecha = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    id_cliente = db.Column(db.Integer, db.ForeignKey('clientes.id_cliente'), nullable=False)

    subtotal = db.Column(DECIMAL(10, 2), nullable=False, default=0.00)
    iva = db.Column(DECIMAL(10, 2), nullable=False, default=0.00)
    total = db.Column(DECIMAL(10, 2), nullable=False, default=0.00)

    estado = db.Column(db.String(20), nullable=False, default='pendiente')

    observaciones = db.Column(db.Text, nullable=False)

    id_usuario_creador = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)

    fecha_creacion = db.Column(db.DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    cliente = db.relationship('Cliente', backref=db.backref('facturas', lazy=True))
    usuario_creador = db.relationship('Usuario', foreign_keys=[id_usuario_creador], backref=db.backref('facturas_creadas', lazy=True))
    detalles = db.relationship('DetalleFactura', backref='factura', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<factura {self.numero_factura}>"
    
    def calcular_totales(self):
        """calcula subtotal, IVA y total basado en los detalles"""
        from decimal import Decimal
        self.subtotal = sum(Decimal(str(detalle.subtotal)) for detalle in self.detalles)
        self.iva = self.subtotal * Decimal('0.21')
        self.total = self.subtotal + self.iva