from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Crear instancia de SQLAlchemy
db = SQLAlchemy()

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

     # Registrar el blueprint de rutas
    from .routes.routesEmpleado import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
