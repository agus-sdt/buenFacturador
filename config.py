import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost/buenaFacturacion'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'admin'  # Cambiar en producción