import pytest

def test_resumen_actividades_camino_1(client):
    """Camino 1. Lista vacía de establecimientos."""

    # Obtener establecimientos
    response = client.get('/establecimientos')

    assert response.status_code == 200
    assert response.get_json() == []


def test_resumen_actividades_camino_2(client, setup_database_sin_serv):
    """Camino 2. Lista vacía de servicios para un establecimiento."""

    # Obtener establecimientos
    response = client.get('/establecimientos')
    establecimientos = response.get_json()

    assert response.status_code == 200
    assert len(establecimientos) > 0 

    # Obtener servicios del establecimiento
    establecimiento = establecimientos[0]
    response = client.get(f'/establecimientos/{establecimiento.get('id')}/servicios')

    assert response.status_code == 200
    assert response.get_json() == []


@pytest.mark.parametrize("datos_resumen,  expected_status_code", [
    ({"fecha_desde": "2024-11-01", "fecha_hasta": ""}, 400),
    ({"fecha_desde": "01-11-2024", "fecha_hasta": "30-11-2024"}, 400),
    ({"fecha_desde": "2024-11-30", "fecha_hasta": "2024-11-01"}, 400),
], ids=["Cadena vacia en fecha", "Formato fecha invalido", "Fecha desde es mayor a fecha hasta"])
def test_resumen_actividades_camino_3(client, setup_database_resumen_actividades, datos_resumen, expected_status_code):
    """Camino 3. Error: datos erróneos del resumen de actividades de empleados por servicio."""

    # Obtener establecimientos
    response = client.get('/establecimientos')
    establecimientos = response.get_json()

    assert response.status_code == 200
    assert len(establecimientos) > 0 

    # Obtener servicios del establecimiento
    establecimiento = establecimientos[0]
    response = client.get(f'/establecimientos/{establecimiento.get('id')}/servicios')
    servicios = response.get_json()

    assert response.status_code == 200
    assert len(servicios) > 1
    
    # Obtener resumen de actividades
    servicio = servicios[0]
    response = client.get(f'/actividades/servicio/{servicio.get('id')}', query_string=datos_resumen)

    assert response.status_code == expected_status_code


def test_resumen_actividades_camino_4(client, setup_database_resumen_actividades):
    """Camino 4. Éxito de la transacción."""

    # Obtener establecimientos
    response = client.get('/establecimientos')
    establecimientos = response.get_json()

    assert response.status_code == 200
    assert len(establecimientos) > 0 

    # Obtener servicios del establecimiento
    establecimiento = establecimientos[0]
    response = client.get(f'/establecimientos/{establecimiento.get('id')}/servicios')
    servicios = response.get_json()

    assert response.status_code == 200
    assert len(servicios) > 1
    
    # Obtener resumen de actividades
    servicio = servicios[0]
    response = client.get(f'/actividades/servicio/{servicio.get('id')}',
        query_string={
            'fecha_desde': '2024-11-01',
            'fecha_hasta': '2024-11-30'
        }
    )

    resumen = response.get_json()

    assert response.status_code == 200

    assert resumen[0]['nombre'] == "Roberto"
    assert resumen[0]['cantidad_guardias_activas'] == 1

    assert resumen[1]['nombre'] == "María"
    assert resumen[1]['cantidad_guardias_activas'] == 1
    assert resumen[1]['cantidad_traslados'] == 1

    assert resumen[2]['nombre'] == "Juan"
    assert resumen[2]['dias_licencia'] == 7
    assert resumen[2]['cantidad_guardias_activas'] == 0
