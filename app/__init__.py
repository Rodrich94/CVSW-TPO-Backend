from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_seeder import FlaskSeeder
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

from config import config  # Importa el archivo config.py

# Crear instancia de SQLAlchemy
db = SQLAlchemy()
seeder = FlaskSeeder()

# Crear función para inicializar la aplicación Flask
def create_app(config_name=None):
    app = Flask(__name__)

    # Determinar el entorno (por defecto: desarrollo)
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])  # Carga la configuración desde config.py

    # Inicializar la base de datos y Flask-Migrate
    db.init_app(app)
    migrate = Migrate(app, db)
    seeder.init_app(app, db)

    # Registrar todos los blueprints
    from .routes import register_blueprints
    register_blueprints(app)

    # Registrar comandos personalizados
    from .models import init_db, populate_db
    app.cli.add_command(init_db)
    app.cli.add_command(populate_db)

    return app
