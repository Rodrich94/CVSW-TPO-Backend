import unittest
from app import create_app, db
from app.models import Traslado, ActividadExtraordinaria
from datetime import datetime

def test_crear_traslado(app_context, setup_database, crear_actividad):
    """Prueba la creación de un traslado"""
    actividad = crear_actividad
    traslado = Traslado(
        id=actividad.id,
        origen="Ciudad A",
        destino="Ciudad B",
        tramo="1",
    )
    db.session.add(traslado)
    db.session.commit()

    # Consultar traslado de la base de datos
    traslado_query = db.session.get(Traslado, actividad.id)
    assert traslado_query is not None
    assert traslado_query.origen == "Ciudad A"
    assert traslado_query.destino == "Ciudad B"
    assert traslado_query.tramo == "1"

def test_eliminar_traslado(app_context, setup_database, crear_actividad):
    """Prueba la eliminación de un traslado"""
    actividad = crear_actividad
    traslado = Traslado(
        id=actividad.id,
        origen="Ciudad A",
        destino="Ciudad B",
        tramo="1",
    )
    db.session.add(traslado)
    db.session.commit()

    db.session.delete(traslado)
    db.session.commit()

    traslado_query = db.session.get(Traslado, actividad.id)
    assert traslado_query is None
