import pytest
from app import create_app, db
from app.models import ActividadExtraordinaria  # Importa modelos necesarios
from datetime import datetime

@pytest.fixture
def app():
    app = create_app(config_name="testing")
    return app

@pytest.fixture
def app_context(app):
    with app.app_context():
        yield app

@pytest.fixture
def setup_database(app_context):
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()

@pytest.fixture
def crear_actividad(app_context, setup_database):
    fecha_ini = datetime.strptime("2024-11-20", "%Y-%m-%d").date()
    fecha_fin = datetime.strptime("2024-11-22", "%Y-%m-%d").date()

    actividad = ActividadExtraordinaria(
        id=1, fecha_ini=fecha_ini, fecha_fin=fecha_fin, estado="Pendiente",
        servicio_id=1, legajo_empleado="1234"
    )
    db.session.add(actividad)
    db.session.commit()
    return actividad




