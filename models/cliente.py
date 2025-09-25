from extensions import db

class Cliente(db.Model):
    __tablename__ = "clientes"

    id_cliente = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f"<cliente {self.nombre}>"