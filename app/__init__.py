# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_seeder import FlaskSeeder
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Crear instancia de SQLAlchemy
db = SQLAlchemy()
seeder = FlaskSeeder()

# Crear función para inicializar la aplicación Flask
def create_app():
    app = Flask(__name__)

    # Configurar la URI de la base de datos desde las variables de entorno
    db_username = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar la base de datos y Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)
    seeder.init_app(app, db)

    # Registrar todos los blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Registramos comandos 'init' y 'populate' para resetear la bd,
    # y hacer la carga de datos de prueba, respectivamente 
    from .models import init_db, populate_db
    app.cli.add_command(init_db)
    app.cli.add_command(populate_db)

    return app
