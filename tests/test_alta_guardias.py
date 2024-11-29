import json
from app.models import Establecimiento


def test_alta_guardias_camino1(client, setup_database):
    """Camino 1. Éxito."""

    # Datos de entrada para las guardias
    guardias = {
        'tipo': 'activa',
        'servicio_id': 1,
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

    # Ejecutar POST /guardias/empleado/
    response = client.post(
        '/guardia/empleado',
        data=json.dumps(guardias),
        content_type='application/json'
    )

    # Agrega las guardia correctamente
    assert response.status_code == 201
    assert response.get_json().get('cantidad_guardias') == 1.5


def test_alta_guardias_camino2(client):
    """Camino 2. Lista vacía de establecimientos."""

    response = client.get('/establecimientos')
    assert response.status_code == 200
    assert response.get_json() == []


def test_alta_guardias_camino3(app, client, setup_database_sin_serv):
    """Camino 3. Lista vacía de servicios."""

    response = client.get('/establecimientos/1/servicios')
    assert response.status_code == 200
    assert response.get_json() == []

    with app.app_context():
        establecimiento = Establecimiento.query.get(1)
        assert establecimiento is not None
        assert len(establecimiento.servicios) == 0


def test_alta_guardias_camino4(client, setup_database):
    """Camino 4. Error al registrar guardias."""

    # Datos de entrada para las guardias
    guardias = {
        'tipo': 'activa',
        'servicio_id': 1,
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

    # Ejecutar POST /guardias/empleado/
    response = client.post(
        '/guardia/empleado',
        data=json.dumps(guardias),
        content_type='application/json'
    )

    # Los datos son correctos, pero no hay un cupo mensual
    assert response.status_code == 400
