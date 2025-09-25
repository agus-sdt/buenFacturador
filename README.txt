Sistema de Facturación (Flask + MySQL + AdminLTE)

Este es un sistema de facturación desarrollado en Python (Flask) con
conexión a MySQL mediante PyMySQL y Front-End con AdminLTE.
El proyecto está pensado para correr en local con XAMPP / MySQL
Workbench, pero puede adaptarse a otros entornos fácilmente.

------------------------------------------------------------------------

Requisitos previos

-   Python 3.9+
-   MySQL (XAMPP, MariaDB o Workbench)
-   Git

------------------------------------------------------------------------

📥 Instalación

1.  Clonar el repositorio

        git clone https://github.com/agus-sdt/buenFacturador.git
        cd buenaFacturacion

2.  Crear un entorno virtual

        python -m venv venv

3.  Activar el entorno virtual

    -   Windows:

            venv\Scripts\activate

    -   Linux / Mac:

            source venv/bin/activate

4.  Instalar dependencias

        pip install -r requirements.txt

------------------------------------------------------------------------

Base de datos

1.  Crear la base de datos en MySQL

        CREATE DATABASE buenaFacturacion;

2.  Importar el esquema desde el archivo .sql

        mysql -u root -p buenaFacturacion < db/buenaFacturacion.sql

        Cambia root y la contraseña si usás otro usuario en MySQL.

3.  Configurar la conexión en config.py (o donde tengas tu string de
    conexión)

        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/buenaFacturacion"

------------------------------------------------------------------------

Ejecutar el proyecto

1.  Asegúrate de tener activado el entorno virtual.

2.  Levantar el servidor Flask:

        flask run

3.  Abrir en el navegador:

        http://127.0.0.1:5000/

4.  En el login puede iniciar con email "admin@gmail.com" password="admin123".

5.  Tambien puede crear un usuario con un gmail y una contraseña.
------------------------------------------------------------------------
