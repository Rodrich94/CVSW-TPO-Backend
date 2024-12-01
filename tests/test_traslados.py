import json
from app import db
from app.models import Establecimiento, Traslado, Servicio


import pytest
import json

@pytest.mark.parametrize(
    "traslado_data, expected_status, expected_error",
    [
        # Caso de éxito
        (
            {
                "origen": "Ciudad A",
                "destino": "Ciudad B",
                "tramo": "1",
                "fecha_inicio": "2024-10-10",
                "fecha_fin": "2024-10-20",
                "empleado_id": "E001",
                "servicio_id": 2
            },
            201,
            None
        ),
        # Faltan campos obligatorios
        (
            {
                "destino": "Ciudad B",
                "tramo": "1",
                "fecha_inicio": "2024-10-10",
                "fecha_fin": "2024-10-20",
                "empleado_id": "E001",
                "servicio_id": 2
            },
            400,
            "El campo 'origen' es requerido."
        ),
        # Fechas inválidas (fecha_fin anterior a fecha_inicio)
        (
            {
                "origen": "Ciudad A",
                "destino": "Ciudad B",
                "tramo": "1",
                "fecha_inicio": "2024-10-20",
                "fecha_fin": "2024-10-10",
                "empleado_id": "E001",
                "servicio_id": 2
            },
            400,
            "La fecha de inicio debe ser menor a la de fin"
        ),
        # Campo tramo vacío
        (
            {
                "origen": "Ciudad A",
                "destino": "Ciudad B",
                "tramo": "",
                "fecha_inicio": "2024-10-10",
                "fecha_fin": "2024-10-20",
                "empleado_id": "E001",
                "servicio_id": 2
            },
            400,
            "El tramo '' no es válido. Debe ser 1 (100km - 180km), 2(181km - 360km) o 3 (mas de 360km)."
        ),
        # Servicio ID no válido
        (
            {
                "origen": "Ciudad A",
                "destino": "Ciudad B",
                "tramo": "1",
                "fecha_inicio": "2024-10-10",
                "fecha_fin": "2024-10-20",
                "empleado_id": "E001",
                "servicio_id": -1
            },
            400,
            "El 'servicio_id' debe ser un número positivo"
        )
    ]
)
def test_crear_traslado_parametrizado(client, setup_database, traslado_data, expected_status, expected_error):
    """
    Prueba parametrizada para el endpoint de creación de traslado.
    """
    response = client.post(
        "/traslado",
        data=json.dumps(traslado_data),
        content_type="application/json"
    )

    assert response.status_code == expected_status

    response_json = response.get_json()

    if expected_status == 201:
        # Verificar que el traslado se creó con éxito
        assert "message" in response_json
        assert response_json["message"] == "Traslado creado exitosamente"
    else:
        # Verificar que se devolvió el error esperado
        assert "error" in response_json
        assert response_json["error"] == expected_error


def test_sin_establecimientos(client):
    """Camino 2. Lista vacía de establecimientos."""
    response = client.get('/establecimientos')
    assert response.status_code == 200
    assert response.get_json() == [] 


def test_sin_servicios_en_establecimiento(client, setup_database_sin_serv,app):

    """Camino 3. Lista vacía de servicios."""

    # Hacer una solicitud al endpoint
    response = client.get('/establecimientos/1/servicios')
    assert response.status_code == 200  # Código de estado esperado
    assert response.get_json() == []  # Respuesta esperada

    # Verificar en la base de datos que no hay servicios
    with app.app_context():
        establecimiento = Establecimiento.query.get(1)  # Obtener el establecimiento por ID
        assert establecimiento is not None
        assert len(establecimiento.servicios) == 0  # Confirmar que no tiene servicios


def test_establecimiento_invalido(client):
    response = client.get('/establecimientos/999/servicios')  # 999 es un ID no existente
    if response.status_code != 201:
        print("Response JSON:", response.get_json())
    assert response.status_code == 404
    assert response.get_json()["error"] == "Establecimiento no encontrado"


def test_obtener_servicio_sin_empleados(client, setup_database):
    """Camino 4. Lista vacía de empleados para el servicio seleccionado."""

    # Hacer una solicitud GET al endpoint /servicios/1/empleados
    response = client.get('/servicios/1/empleados')

    # Verificar que el código de respuesta sea 200 (OK)
    assert response.status_code == 200

    # Verificar que la respuesta sea una lista vacía, ya que no hay empleados asociados al servicio
    assert response.get_json() == []  # La respuesta debe ser una lista vacía

    # Verificar en la base de datos que el servicio con id 1 no tiene empleados
    servicio = Servicio.query.get(1)
    assert servicio is not None  # Asegurarse de que el servicio existe
    assert len(servicio.empleados) == 0  # Confirmar que no tiene empleados asociados


def test_sin_empleados_para_servicio(client, setup_database):

    """Camino 4. Error al registrar guardias."""

    traslado_data = {
        "origen": "Ciudad A",
        "destino": "Ciudad B",
        "tramo": "1",
        "fecha_inicio": "2024-11-01",
        "fecha_fin": "2024-11-02",
        "empleado_id": "E003",  
        "servicio_id": 1  
    }
    response = client.post('/traslado', json=traslado_data)
    if response.status_code != 201:
        print("Response JSON:", response.get_json())
    assert response.status_code == 400
    assert "error" in response.get_json()



def test_obtener_traslados(client, setup_traslados):
    """Test para obtener traslados"""
    
    # Realizar la petición GET a la ruta que devuelve todos los traslados
    response = client.get('/traslados')

    # Verificar que el estado de la respuesta es 200 OK
    assert response.status_code == 200
    
    # Verificar que el primer traslado devuelto tenga la información correcta
    assert len(response.json) > 0
    assert response.json[0]['origen'] == 'Ciudad A'
    assert response.json[0]['destino'] == 'Ciudad B'



def test_borrar_traslado(client, setup_traslados):
    """
    Prueba para verificar que se elimina correctamente un traslado por su ID.
    """
    traslado_id = 1

    # Verificar que el traslado existe antes de la eliminación
    response_get = client.get(f"/traslado/{traslado_id}")
    assert response_get.status_code == 200  # El traslado existe
    traslado = response_get.get_json()
    assert traslado['traslado_id'] == traslado_id

    # Enviar solicitud DELETE al endpoint
    response_delete = client.delete(f"/traslado/{traslado_id}")
    assert response_delete.status_code == 200  # Verificar que la eliminación fue exitosa

    # Verificar el contenido de la respuesta (si incluye un mensaje)
    mensaje = response_delete.get_json()
    assert "message" in mensaje  # Verificar que la clave correcta existe
    assert mensaje["message"] == f"Traslado con ID {traslado_id} eliminado exitosamente"

    # Intentar obtener nuevamente el traslado eliminado
    response_get_after = client.get(f"/traslado/{traslado_id}")
    assert response_get_after.status_code == 404  # El traslado ya no debería existir

def test_borrar_traslado_no_encontrado(client):
    """
    Prueba para verificar que se maneja correctamente el caso de un traslado no encontrado.
    """
    traslado_id = 999  # ID de traslado que no existe en la base de datos

    # Intentar eliminar un traslado inexistente
    response_delete = client.delete(f"/traslado/{traslado_id}")
    
    # Verificar que el código de estado sea 404 (no encontrado)
    assert response_delete.status_code == 404

    # Verificar el contenido de la respuesta (mensaje de error)
    mensaje = response_delete.get_json()
    assert "error" in mensaje  # Verificar que la clave "error" existe
    assert mensaje["error"] == "Traslado no encontrado"