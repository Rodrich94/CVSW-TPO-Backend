import json
from app import db
from app.models import Establecimiento, DiagramaMensual, ActividadDiagrama
import pytest
from datetime import date

@pytest.mark.parametrize(
    "data, expected_error",
    [
        ({"mes": 13, "anio": 2024, "servicio_id": 2}, "El mes debe estar entre 1 y 12"),  # Mes inválido
        ({"mes": 0, "anio": 2023, "servicio_id": 2}, "El mes debe estar entre 1 y 12"),   # Mes inválido
        ({"mes": 1, "anio": -2023, "servicio_id": 2}, "El año debe ser un valor positivo"),  # Año inválido
        ({"mes": 5, "anio": -2023, "servicio_id": 2}, "El año debe ser un valor positivo"),  # Año inválido
        ({"mes": 1, "anio": "asdasd", "servicio_id": 2}, "El mes y el año deben ser enteros positivos"),  # Año no entero
        ({"mes": "asdasdasd", "anio": 2024, "servicio_id": 2}, "El mes y el año deben ser enteros positivos"),  # Mes no entero
    ]
)
def test_error_dato_diagrama(client, setup_traslados, setup_database, expected_error, data):
    """
    Camino 3. Prueba parametrizada para verificar que se devuelva un error cuando se envían datos inválidos o incompletos al crear un diagrama.
    """
    response = client.post(
        '/diagrama',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    # Verificar que el estado sea 400
    assert response.status_code == 400

    # Verificar el mensaje de error
    response_data = response.get_json()
    assert "error" in response_data
    assert response_data["error"] == expected_error


@pytest.mark.parametrize(
    "mes, anio, servicio_id, expected_status, expected_error",
    [
        # Casos inválidos para mes y año
        (13, 2024, 2, 400, "Fechas generadas son inválidas"),  # Mes inválido
        (0, 2023, 2, 400, "Mes y año son requeridos"),    # Mes inválido
        (1, -2023, 2, 400, "El año debe ser un valor positivo"),  # Año inválido
        (5, -2023, 2, 400, "El año debe ser un valor positivo"),  # Año inválido
        (1, "asdasd", 2, 400, "Mes y año son requeridos"),  # Año no entero
        ("asdasdasd", 2024, 2, 400, "Mes y año son requeridos"),  # Mes no entero
    ]
)
def test_obtener_diagramas_filtrados_error(client, mes, anio, servicio_id, expected_status, expected_error):
    """
    Camino 3. Prueba para verificar que se devuelven errores cuando los parámetros mes y año son incorrectos.
    """
    response = client.get(
        "/diagramas/filtrados",
        query_string={"mes": mes, "anio": anio, "servicio_id": servicio_id}
    )

    # Verificar que la respuesta sea el código de estado esperado
    assert response.status_code == expected_status

    # Verificar que el error devuelto sea el esperado
    response_data = response.get_json()
    assert "error" in response_data
    assert response_data["error"] == expected_error


def test_sin_establecimientos(client):
    """Camino 1. Lista vacía de establecimientos."""
    response = client.get('/establecimientos')
    assert response.status_code == 200
    assert response.get_json() == [] 


def test_sin_servicios_en_establecimiento(client, setup_database_sin_serv, app):
    """Camino 2. Lista vacía de servicios."""
    # Hacer una solicitud al endpoint
    response = client.get('/establecimientos/1/servicios')
    assert response.status_code == 200  # Código de estado esperado
    assert response.get_json() == []  # Respuesta esperada

    # Verificar en la base de datos que no hay servicios
    with app.app_context():
        establecimiento = Establecimiento.query.get(1)  # Obtener el establecimiento por ID
        assert establecimiento is not None
        assert len(establecimiento.servicios) == 0  # Confirmar que no tiene servicios


def test_alta_diagrama_mensual(client, setup_traslados, setup_database, app):
    """
    Camino 5. Prueba para verificar el alta de un diagrama mensual con datos válidos
    y su obtención mediante el endpoint correspondiente.
    """
    # Datos válidos para crear un diagrama mensual
    datos_diagrama = {
        "mes": 9,          # Septiembre
        "anio": 2024,       # Año 2024
        "servicio_id": 2    # Servicio previamente configurado en los traslados
    }

    # Enviar solicitud POST al endpoint para crear el diagrama
    response = client.post(
        "/diagrama",
        data=json.dumps(datos_diagrama),
        content_type="application/json"
    )

    # Verificar que la respuesta sea 201 CREATED
    assert response.status_code == 201

    # Verificar que la respuesta JSON contiene el mensaje esperado y el id del diagrama
    response_data = response.get_json()
    assert "message" in response_data
    assert response_data["message"] == "Diagrama creado exitosamente"
    assert "diagrama_id" in response_data

    # Obtener el ID del diagrama creado
    diagrama_id = response_data["diagrama_id"]

    # Verificar que se puede obtener el diagrama creado mediante el endpoint GET
    response_get = client.get(f"/diagrama/{diagrama_id}")
    assert response_get.status_code == 200

    # Verificar que la respuesta contiene los datos correctos del diagrama
    response_data_get = response_get.get_json()
    assert response_data_get is not None
    assert response_data_get["id"] == diagrama_id
    assert response_data_get["servicio"] == "Traumatología"

    with app.app_context():
        # Verificar el diagrama creado en la base de datos
        diagrama = DiagramaMensual.query.get(diagrama_id)
        assert diagrama is not None
        assert diagrama.fecha_ini == date(2024, 9, 16)
        assert diagrama.fecha_fin == date(2024, 10, 15)
        assert diagrama.servicio_id == 2

        # Verificar que las actividades asociadas sean correctas
        actividades_asociadas = ActividadDiagrama.query.filter_by(diagrama_id=diagrama_id).all()
        assert len(actividades_asociadas) > 0  # Asegurarse de que hay actividades asociadas


def test_obtener_diagramas_filtrados(client, setup_datos_diagramas):
    response = client.get(
        "/diagramas/filtrados",
        query_string={"mes": 9, "anio": 2024, "servicio_id": 2}
    )
    assert response.status_code == 200

    data = response.get_json()
    for diagrama in data:
        assert diagrama['servicio_id'] == 2  # Verificar el ID dentro del objeto `servicio_id`
        if diagrama['actividades_extraordinarias']:
            for actividad in diagrama['actividades_extraordinarias']:
                assert 'id' in actividad
                assert 'fecha_ini' in actividad
                assert 'fecha_fin' in actividad
                assert 'nombre_empleado' in actividad
                assert 'apellido_empleado' in actividad
    assert len(data) > 0


def test_eliminar_diagrama(client, setup_traslados, app):
    """
    Camino para verificar la eliminación de un diagrama mensual
    y su ausencia en la base de datos.
    """
    # Primero, creamos un diagrama para poder eliminarlo luego
    datos_diagrama = {
        "mes": 9,          # Septiembre
        "anio": 2024,      # Año 2024
        "servicio_id": 2   # Servicio previamente configurado en los traslados
    }

    # Enviar solicitud POST al endpoint para crear el diagrama
    response_post = client.post(
        "/diagrama",
        data=json.dumps(datos_diagrama),
        content_type="application/json"
    )

    # Verificar que la creación fue exitosa
    assert response_post.status_code == 201
    response_data_post = response_post.get_json()
    diagrama_id = response_data_post["diagrama_id"]

    # Verificar que el diagrama fue creado en la base de datos
    with app.app_context():
        diagrama = DiagramaMensual.query.get(diagrama_id)
        assert diagrama is not None

    # Enviar solicitud DELETE al endpoint para eliminar el diagrama
    response_delete = client.delete(f"/diagrama/{diagrama_id}")

    # Verificar que la respuesta sea 200 OK y contenga el mensaje esperado
    assert response_delete.status_code == 200
    response_data_delete = response_delete.get_json()
    assert "message" in response_data_delete
    assert response_data_delete["message"] == "Diagrama eliminado exitosamente"

    # Verificar que el diagrama ha sido eliminado de la base de datos
    with app.app_context():
        diagrama_eliminado = DiagramaMensual.query.get(diagrama_id)
        assert diagrama_eliminado is None  # El diagrama ya no debe existir

    # Intentar obtener el diagrama eliminado
    response_get = client.get(f"/diagrama/{diagrama_id}")
    assert response_get.status_code == 404  # Debería devolver 404 porque el diagrama fue eliminado
    response_data_get = response_get.get_json()
    assert "error" in response_data_get
    assert response_data_get["error"] == "Diagrama no encontrado"


def test_obtener_diagramas(client, setup_datos_diagramas, app):
    """
    Verifica que se obtienen todos los diagramas correctamente.
    """
    # En este caso, el fixture setup_datos_diagramas se encarga de agregar dos diagramas en la base de datos.
    
    # Enviar solicitud GET para obtener todos los diagramas
    response_get = client.get("/diagramas")

    # Verificar que la respuesta sea 200 OK
    assert response_get.status_code == 200
    response_data_get = response_get.get_json()

    # Verificar que los diagramas creados estén en la respuesta
    assert isinstance(response_data_get, list)
    assert len(response_data_get) > 0  # Asegurarse de que hay diagramas en la respuesta

    # Comprobar que los diagramas específicos están en la respuesta
    diagrama_1_encontrado = False
    diagrama_2_encontrado = False
    for diagrama in response_data_get:
        if diagrama["servicio"] == "Traumatología":  # Cambia esto según el nombre real del servicio
            if diagrama["fecha_ini"] == "2024-09-16" and diagrama["fecha_fin"] == "2024-10-15":
                diagrama_1_encontrado = True
            if diagrama["fecha_ini"] == "2024-10-16" and diagrama["fecha_fin"] == "2024-11-15":
                diagrama_2_encontrado = True

    assert diagrama_1_encontrado
    assert diagrama_2_encontrado
    # Verificar que los diagramas están en la base de datos
    with app.app_context():
        diagrama_1 = DiagramaMensual.query.filter_by(fecha_ini='2024-09-16').first()
        assert diagrama_1 is not None
        diagrama_2 = DiagramaMensual.query.filter_by(fecha_ini='2024-10-16').first()
        assert diagrama_2 is not None
