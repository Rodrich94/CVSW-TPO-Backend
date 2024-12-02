import pytest

def test_cambio_empleado_guardia_camino_1(client):
    """Camino 1. Lista vacía de establecimientos."""

    # Obtener establecimientos
    response = client.get('/establecimientos')

    assert response.status_code == 200
    assert response.get_json() == []


def test_cambio_empleado_guardia_camino_2(client, setup_database_sin_serv):
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

@pytest.mark.parametrize("servicio_id, tipo, datos_guardia, expected_status_code", [
    (1, "Activaa", {"fecha_guardia": "2024-11-11", "legajo_empleado": "E002"}, 400),
    (1, "Activ", {"fecha_guardia": "2024-11-11", "legajo_empleado": "E002"}, 400),
    (1, "Activa", {"fecha_guardia": "2024-17-11", "legajo_empleado": "E002"}, 400),
    (1, "Activa", {"fecha_guardia": "2024-11-11", "legajo_empleado": "Emp002"}, 400),
    (0, "Activa", {"fecha_guardia": "2024-11-11", "legajo_empleado": "E002"}, 404),
    (2, "Activa", {"fecha_guardia": "2024-11-11", "legajo_empleado": "E002"}, 404),
], ids=["Tipo de guardia invalido-1", "Tipo de guardia invalido-2", "Fecha invalida (mes)", "Formato legajo invalido", "ID servicio invalido", "Servicio inexistente"])
def test_cambio_empleado_guardia_camino_3(client, setup_database_cambio_empleado_guardia, servicio_id, tipo, datos_guardia, expected_status_code):
    """Camino 3. Error: datos erróneos de la guardia."""

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
    assert len(servicios) == 1

    # Obtener guardias de un servicio
    response = client.get(f'/guardias/servicio-tipo/{servicio_id}/{tipo}', query_string=datos_guardia)
    
        
    assert response.status_code == expected_status_code 


@pytest.mark.parametrize("datos_empleado,  expected_status_code", [
    ({"legajo_empleado": "E003"}, 400),
    ({"legajo_empleado": "E3"}, 400),
    ({"legajo_empleado": "123"}, 400),
    ({"legajo_empleado": ""}, 400),
], ids=["Formato legajo invalido-1", "Formato legajo invalido-2", "Formato legajo invalido-3", "Cadena vacia en legajo"])
def test_cambio_empleado_guardia_camino_4(client, setup_database_cambio_empleado_guardia, datos_empleado, expected_status_code):
    """Camino 4. Error: datos erróneos del empleado o la guardia al confirmar la transacción."""

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
    assert len(servicios) == 1

    # Obtener guardias de un servicio
    servicio = servicios[0]
    datos_guardia = {
        "fecha_guardia": "2024-11-11",
        "legajo_empleado": "E002"
    }
    response = client.get(f'/guardias/servicio-tipo/{servicio.get('id')}/activa', query_string=datos_guardia)
    guardias = response.get_json()

    assert response.status_code == 200
    assert len(guardias) > 0
    
    for guardia in guardias:
        assert guardia.get('estado') == 'Pendiente'
      
    # Cambiar empleado de la guardia
    guardia = guardias[0]
    response = client.put(f'/guardia/cambiar-empleado/{guardia.get('id')}', json=datos_empleado)

    assert response.status_code == expected_status_code



def test_cambio_empleado_guardia_camino_5(client, setup_database_cambio_empleado_guardia):
    """Camino 5. Éxito de la transacción"""

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
    assert len(servicios) == 1

    # Obtener guardias de un servicio
    servicio = servicios[0]
    datos_guardia = {
        "fecha_guardia": "2024-11-11",
        "legajo_empleado": "E002"
    }
    response = client.get(f'/guardias/servicio-tipo/{servicio.get('id')}/activa', query_string=datos_guardia)
    guardias = response.get_json()

    assert response.status_code == 200
    assert len(guardias) > 0
    
    for guardia in guardias:
        assert guardia.get('estado') == 'Pendiente'
      
    # Cambiar empleado de la guardia
    guardia = guardias[0]
    datos_empleado = {
        "legajo_empleado": "E002"
    }
    response = client.put(f'/guardia/cambiar-empleado/{guardia.get('id')}', json=datos_empleado)

    assert response.status_code == 201
    