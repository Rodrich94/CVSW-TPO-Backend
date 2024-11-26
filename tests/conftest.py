import pytest
from app import create_app, db
from app.models import Establecimiento, Servicio, Empleado

# Fixture para la aplicación de pruebas
@pytest.fixture
def app():
    app = create_app('testing')  # Usar configuración de pruebas
    with app.app_context():
        db.create_all()  # Crear todas las tablas en la base de datos
        yield app
        db.session.remove()
        db.drop_all()  # Limpiar después de las pruebas

# Fixture para el cliente de pruebas
@pytest.fixture
def client(app):
    return app.test_client()

# Fixture para agregar datos de prueba en la base de datos
@pytest.fixture
def setup_database(app):
    """Fixture para configurar los datos de prueba en la base de datos"""
    with app.app_context():
        # Limpiar la base de datos antes de agregar nuevos datos
        db.drop_all()
        db.create_all()

        # Agregar 4 establecimientos
        establecimiento1 = Establecimiento(nombre='Hospital Central', ubicacion='Neuquén')
        establecimiento2 = Establecimiento(nombre='Clínica del Sur', ubicacion='Plottier')
        establecimiento3 = Establecimiento(nombre='Sanatorio Norte', ubicacion='Centenario')
        establecimiento4 = Establecimiento(nombre='Centro Médico Este', ubicacion='Zapala')

        db.session.add_all([establecimiento1, establecimiento2, establecimiento3, establecimiento4])

        # Agregar 4 servicios para los establecimientos
        servicio1 = Servicio(nombre='Cardiología', establecimiento=establecimiento1)
        servicio2 = Servicio(nombre='Traumatología', establecimiento=establecimiento2)
        servicio3 = Servicio(nombre='Pediatría', establecimiento=establecimiento3)
        servicio4 = Servicio(nombre='Emergencias', establecimiento=establecimiento4)

        db.session.add_all([servicio1, servicio2, servicio3, servicio4])

        # Agregar 4 empleados para los servicios
        empleado1 = Empleado(legajo='E001', nombre='Roberto', apellido='Bolaños', rol='Autorizante', servicio=servicio1)
        empleado2 = Empleado(legajo='E002', nombre='María', apellido='Lopez', rol='Autorizante', servicio=servicio2)
        empleado3 = Empleado(legajo='E003', nombre='Juan', apellido='Pérez', rol='Gestion', servicio=servicio3)
        empleado4 = Empleado(legajo='E004', nombre='Ana', apellido='González', rol='Gestion', servicio=servicio4)

        db.session.add_all([empleado1, empleado2, empleado3, empleado4])

        # Confirmar los cambios
        db.session.commit()

        yield db

        # Limpiar después de la prueba (opcional)
        db.session.remove()
        db.drop_all()
