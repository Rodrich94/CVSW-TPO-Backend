import json
from app import create_app, db
from app.models import ActividadExtraordinaria, Traslado

def test_alta_traslado(client, setup_database):
    """Prueba el endpoint de alta de traslado"""

    # Datos de entrada para el traslado
    traslado_data = {
        "origen": "Ciudad A",
        "destino": "Ciudad B",
        "tramo": "1",
        "fecha_inicio": "2024-10-25",
        "fecha_fin": "2024-10-20",
        "empleado_id": "E001",
        "servicio_id": 1
    }

    # Enviar POST al endpoint /traslado
    response = client.post(
        "/traslado",
        data=json.dumps(traslado_data),
        content_type="application/json"
    )

    # Imprimir la respuesta JSON si el código de estado no es 201
    if response.status_code != 400:
        print("Error Response JSON:", response.get_json())

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