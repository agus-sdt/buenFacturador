import os

class Config:
#    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Natasha2033@localhost:3306/buenafacturacion'
#    SQLALCHEMY_TRACK_MODIFICATIONS = False
#    SECRET_KEY = 'admin'  

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "buenafacturacion.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "admin"