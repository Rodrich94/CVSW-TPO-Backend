

def test_consulta_actividades_camino1(client, setup_guardias):
    """Camino 1. Éxito."""

    # Obtener empleado
    response = client.get('/empleado/E001')

    assert response.status_code == 200

    # Obtener actividades con éxito
    legajo = response.get_json().get('legajo')
    response = client.get(
        f'/actividades/empleado/{legajo}',
        query_string={
            'fecha_desde': '2024-11-01',
            'fecha_hasta': '2024-11-30'
        }
    )

    assert response.status_code == 200
    assert len(response.get_json()) == 1
    assert b'E001' in response.data
    assert b'activa' in response.data


def test_consulta_actividades_camino2(client):
    """Camino 2: Error al obtener empleado."""

    # Obtener empleado
    response = client.get('/empleado/E000')

    assert response.status_code == 404


def test_consulta_actividades_camino3(client, setup_database):
    """Camino 3: Error al obtener actividades."""

    # Obtener empleado
    response = client.get('/empleado/E001')

    assert response.status_code == 200

    # Obtener actividades con error (no tiene actividades en el rango de fechas)
    legajo = response.get_json().get('legajo')
    response = client.get(
        f'/actividades/empleado/{legajo}',
        query_string={
            'fecha_desde': '2024-12-01',
            'fecha_hasta': '2024-12-31'
        }
    )

    assert response.status_code == 200
    assert response.get_json() == []
