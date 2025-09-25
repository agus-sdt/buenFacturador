from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.now, nullable=False)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password_text):
        """Hashea y guarda la contraseña"""
        self.password = generate_password_hash(password_text)

    def check_password(self, password_text):
        """verifica si la contraseña es correcta"""
        return check_password_hash(self.password, password_text)
    
    def is_active(self):
        """flask-login: usuario activo"""
        return self.activo
    
    def get_id(self):
        """flask-login: ID del usuario"""
        return str(self.id_usuario)

    def __repr__(self):
        return f"<Usuario {self.email}>"