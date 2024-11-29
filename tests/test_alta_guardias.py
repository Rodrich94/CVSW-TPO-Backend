import json
from app.models import Establecimiento


def test_alta_guardias_camino1(client, setup_database):
    """Camino 1. Éxito."""

    # Obtener establecimientos
    response = client.get('/establecimientos')
    establecimientos = response.get_json()

    assert response.status_code == 200
    assert len(establecimientos) > 0

    # Seleccionar servicio
    establecimiento = establecimientos[0]
    response = client.get(f'/establecimientos/{establecimiento.get('id')}/servicios')
    servicios = response.get_json()

    assert response.status_code == 200
    assert len(servicios) > 0

    # Datos de entrada para las guardias
    servicio = servicios[0]
    guardias = {
        'tipo': 'activa',
        'servicio_id': servicio.get('id'),
        'legajo_empleado': 'E001',
        'periodo': ['2024-09-16', '2024-10-15'],
        'guardias': [
            {
                'fecha_ini': '2024-09-16',
                'fecha_fin': '2024-09-17',
                'duracion': 24
            },
            {
                'fecha_ini': '2024-09-20',
                'fecha_fin': '2024-09-21',
                'duracion': 12
            }
        ]
    }

    # Alta de guardias con éxito
    response = client.post(
        '/guardia/empleado',
        data=json.dumps(guardias),
        content_type='application/json'
    )

    assert response.status_code == 201
    assert response.get_json().get('cantidad_guardias') == 1.5


def test_alta_guardias_camino2(client):
    """Camino 2. Lista vacía de establecimientos."""

    # Obtener establecimientos
    response = client.get('/establecimientos')

    assert response.status_code == 200
    assert response.get_json() == []


def test_alta_guardias_camino3(app, client, setup_database_sin_serv):
    """Camino 3. Lista vacía de servicios."""

    # Obtener establecimientos
    response = client.get('/establecimientos')
    establecimientos = response.get_json()

    assert response.status_code == 200
    assert len(establecimientos) > 0

    # Seleccionar servicio
    establecimiento = establecimientos[0]
    response = client.get(f'/establecimientos/{establecimiento.get('id')}/servicios')

    assert response.status_code == 200
    assert response.get_json() == []

    with app.app_context():
        establecimiento = Establecimiento.query.get(establecimiento.get('id'))
        assert establecimiento is not None
        assert len(establecimiento.servicios) == 0


def test_alta_guardias_camino4(client, setup_database):
    """Camino 4. Error al registrar guardias."""

    # Obtener establecimientos
    response = client.get('/establecimientos')
    establecimientos = response.get_json()

    assert response.status_code == 200
    assert len(establecimientos) > 0

    # Seleccionar servicio
    establecimiento = establecimientos[0]
    response = client.get(f'/establecimientos/{establecimiento.get('id')}/servicios')
    servicios = response.get_json()

    assert response.status_code == 200
    assert len(servicios) > 0

    # Datos de entrada para las guardias
    servicio = servicios[0]
    guardias = {
        'tipo': 'activa',
        'servicio_id': servicio.get('id'),
        'legajo_empleado': 'E001',
        'periodo': ['2024-09-16', '2024-10-15'],
        'guardias': [
            {
                'fecha_ini': '2025-01-01',
                'fecha_fin': '2025-01-03',
                'duracion': 24
            }
        ]
    }

    # Alta de guardias con error (no hay un cupo mensual para el año 2025)
    response = client.post(
        '/guardia/empleado',
        data=json.dumps(guardias),
        content_type='application/json'
    )

    assert response.status_code == 400
