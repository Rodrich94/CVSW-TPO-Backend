

def test_consulta_actividades_camino1(client, setup_database):
    """Camino 1. Éxito."""

    response = client.get(
        '/actividades/empleado/E001',
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

    response = client.get('/empleado/E000')
    assert response.status_code == 404


def test_consulta_actividades_camino3(client, setup_database):
    """Camino 3: Error al obtener actividades."""

    response = client.get(
        '/actividades/empleado/E001',
        query_string={
            'fecha_desde': '2024-12-01',
            'fecha_hasta': '2024-12-31'
        }
    )

    assert response.status_code == 200
    assert response.get_json() == []
