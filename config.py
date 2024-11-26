import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    """Configuraciones base comunes a todos los entornos"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta-predeterminada')
    TESTING = False

class DevelopmentConfig(Config):
    """Configuraciones para desarrollo"""
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    DEBUG = True

class TestingConfig(Config):
    """Configuraciones para pruebas"""
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME_T')}:{os.getenv('DB_PASSWORD_T')}@"
        f"{os.getenv('DB_HOST_T')}:{os.getenv('DB_PORT_T')}/{os.getenv('DB_NAME_T')}"
    )
    TESTING = True
    DEBUG = False

class ProductionConfig(Config):
    """Configuraciones para producción"""
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    DEBUG = False

# Mapeo de entornos
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
