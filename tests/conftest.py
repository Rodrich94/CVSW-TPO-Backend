import pytest
from app import create_app, db
from app.models import ActividadExtraordinaria, CupoMensual, Guardia, Establecimiento, Servicio, Empleado, DiagramaMensual
import json
from datetime import date


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
        empleado1 = Empleado(legajo='E001', nombre='Roberto', apellido='Bolaños', rol='Autorizante', servicio=servicio2)
        empleado2 = Empleado(legajo='E002', nombre='María', apellido='Lopez', rol='Autorizante', servicio=servicio2)
        empleado3 = Empleado(legajo='E003', nombre='Juan', apellido='Pérez', rol='Gestion', servicio=servicio3)
        empleado4 = Empleado(legajo='E004', nombre='Ana', apellido='González', rol='Gestion', servicio=servicio4)

        db.session.add_all([empleado1, empleado2, empleado3, empleado4])

        # Agregar un cupo CupoMensual
        cupo_mensual = CupoMensual(fecha_ini='2024-01-01',
                                   fecha_fin='2024-12-31',
                                   total=100,
                                   remanente=100,
                                   servicio_id=1,
                                   legajo_autorizante='E001')
        db.session.add(cupo_mensual)
        db.session.flush()

        # Agregar una guardia
        nueva_actividad = ActividadExtraordinaria(
            fecha_ini='2024-11-11',
            fecha_fin='2024-11-12',
            estado='Pendiente',
            servicio_id=1,
            legajo_empleado='E001'
        )
        db.session.add(nueva_actividad)
        db.session.flush()

        nueva_guardia = Guardia(
            id=nueva_actividad.id,
            duracion=24,
            tipo='activa',
            cupo_mensual_id=cupo_mensual.id
        )
        db.session.add(nueva_guardia)
        db.session.flush()

        # Confirmar los cambios
        db.session.commit()

        yield db

        # Limpiar después de la prueba (opcional)
        db.session.remove()
        db.drop_all()


@pytest.fixture
def setup_database_sin_serv(app):
    """Fixture para configurar los datos de prueba en la base de datos sin servicios."""
    with app.app_context():
        # Limpiar la base de datos antes de agregar nuevos datos
        db.drop_all()
        db.create_all()

        # Agregar 4 establecimientos sin servicios
        establecimiento1 = Establecimiento(nombre='Hospital Central', ubicacion='Neuquén')

        db.session.add_all([establecimiento1])
        db.session.commit()
        yield db

        # Limpiar después de la prueba (opcional)
        db.session.remove()
        db.drop_all()


@pytest.fixture
def setup_traslados(setup_database, app, client):
    """Fixture que agrega varios traslados a la base de datos después de configurar los datos de prueba."""
    with app.app_context():
        # Lista de traslados de prueba
        traslados_data = [
            {
                "origen": "Ciudad A",
                "destino": "Ciudad B",
                "tramo": "1",
                "fecha_inicio": "2024-10-10",
                "fecha_fin": "2024-10-20",
                "empleado_id": "E001",
                "servicio_id": 2
            },
            {
                "origen": "Ciudad C",
                "destino": "Ciudad D",
                "tramo": "2",
                "fecha_inicio": "2024-11-01",
                "fecha_fin": "2024-11-15",
                "empleado_id": "E002",
                "servicio_id": 2
            },
        ]

        # Enviar múltiples solicitudes POST al endpoint /traslado
        for traslado_data in traslados_data:
            response = client.post(
                "/traslado",
                data=json.dumps(traslado_data),
                content_type="application/json"
            )

            # Verificar que la respuesta sea exitosa (por ejemplo, código 201)
            if response.status_code != 201:
                print("Error al agregar traslado:", traslado_data)
                print("Response JSON:", response.get_json())

            assert response.status_code == 201

        # Yield para usar la base de datos con los traslados en los tests
        yield db

        # Limpiar la base de datos después de la prueba (opcional)
        db.session.remove()


@pytest.fixture
def setup_datos_diagramas(app, client, setup_traslados):
    """
    Fixture para preparar datos de prueba relacionados con servicios, establecimientos y diagramas.
    """
    with app.app_context():
        # Crear los diagramas utilizando el endpoint de alta diagrama (a través del cliente)
        diagramas_data = [
            {
                "mes": 9,          # Septiembre
                "anio": 2024,       # Año 2024
                "servicio_id": 2    # Servicio previamente configurado en los traslados
            },
            {
                "mes": 10,          # Octubre
                "anio": 2024,       # Año 2024
                "servicio_id": 2    # Servicio previamente configurado en los traslados
            },
        ]

        # Enviar solicitudes POST al endpoint /diagrama para agregar los diagramas
        for diagrama_data in diagramas_data:
            response = client.post(
                "/diagrama",  # Ruta para crear un nuevo diagrama
                data=json.dumps(diagrama_data),
                content_type="application/json"
            )

            # Verificar que la respuesta sea exitosa (código 201)
            assert response.status_code == 201, f"Error al agregar diagrama: {diagrama_data}"

        # Commit a la base de datos para asegurar que los diagramas sean persistidos
        db.session.flush()  # Flush para asegurar que los cambios se reflejan inmediatamente

        yield db  # Permite usar los datos durante los tests

        # Limpiar la base de datos después de los tests
        db.session.remove()
