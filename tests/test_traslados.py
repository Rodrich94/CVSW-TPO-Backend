import json
from app import db
from app.models import Establecimiento, Traslado, Servicio


def test_alta_traslado(client, setup_database):
    """Prueba el endpoint de alta de traslado"""

    # Datos de entrada para el traslado
    traslado_data = {
        "origen": "Ciudad A",
        "destino": "Ciudad B",
        "tramo": "1",
        "fecha_inicio": "2024-10-10",
        "fecha_fin": "2024-10-20",
        "empleado_id": "E001",
        "servicio_id": 2
    }

    # Enviar POST al endpoint /traslado
    response = client.post(
        "/traslado",
        data=json.dumps(traslado_data),
        content_type="application/json"
    )

    # Imprimir la respuesta JSON si el código de estado no es 201
    if response.status_code != 400:
        print("Response JSON:", response.get_json())

    # Verificar que el código de respuesta sea 201 (Creado)
    assert response.status_code == 201

    # Verificar el mensaje en la respuesta
    response_json = response.get_json()
    assert response_json["message"] == "Traslado creado exitosamente"

    # Verificar que el traslado fue creado en la base de datos
    traslado = db.session.query(Traslado).filter_by(origen="Ciudad A", destino="Ciudad B").first()
    assert traslado is not None
    assert traslado.tramo == "1"
    assert traslado.actividad is not None  # Verificar relación con ActividadExtraordinaria


def test_sin_establecimientos(client):
    response = client.get('/establecimientos')
    assert response.status_code == 200
    assert response.get_json() == [] 


def test_sin_servicios_en_establecimiento(client, setup_database_sin_serv,app):
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


def test_sin_empleados_para_servicio(client, setup_database):
    traslado_data = {
        "origen": "Ciudad A",
        "destino": "Ciudad B",
        "tramo": "1",
        "fecha_inicio": "2024-11-01",
        "fecha_fin": "2024-11-02",
        "empleado_id": "E003",  # Empleado inexistente
        "servicio_id": 1  # Asume que este ID existe
    }
    response = client.post('/traslado', json=traslado_data)
    if response.status_code != 201:
        print("Response JSON:", response.get_json())
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_obtener_empleados_servicio_sin_empleados(client, setup_database):
    """Prueba el endpoint de obtener empleados de un servicio sin empleados asociados"""

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


def test_obtener_traslados(client, setup_traslados):
    """Test para obtener traslados"""
    
    # Realizar la petición GET a la ruta que devuelve todos los traslados
    response = client.get('/traslados')

    # Verificar que el estado de la respuesta es 200 OK
    assert response.status_code == 200
    
    # Verificar que el primer traslado devuelto tenga la información correcta
    assert len(response.json) > 0
    assert response.json[0]['origen'] == 'Hospital Central'
    assert response.json[0]['destino'] == 'Clínica del Sur'
