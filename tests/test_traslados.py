import unittest
from app import create_app, db
from app.models import Traslado, ActividadExtraordinaria
from datetime import datetime

class TestTraslados(unittest.TestCase):
    """Test para el modelo Traslados"""

    def setUp(self):
        """Configura el entorno de prueba"""
        self.app = create_app(config_name="testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Crear datos iniciales para las pruebas con fechas convertidas a tipo date
        fecha_ini = datetime.strptime("2024-11-20", "%Y-%m-%d").date()
        fecha_fin = datetime.strptime("2024-11-22", "%Y-%m-%d").date()

        self.actividad = ActividadExtraordinaria(
            id=1, fecha_ini=fecha_ini, fecha_fin=fecha_fin, estado="Pendiente",
            servicio_id=1, legajo_empleado="1234"
        )
        db.session.add(self.actividad)
        db.session.commit()

    def tearDown(self):
        """Limpia la base de datos después de cada prueba"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_crear_traslado(self):
        """Prueba la creación de un traslado"""
        traslado = Traslado(
            id=self.actividad.id,
            origen="Ciudad A",
            destino="Ciudad B",
            tramo="1"
        )
        db.session.add(traslado)
        db.session.commit()

        # Consultar traslado de la base de datos
        traslado_query = Traslado.query.get(self.actividad.id)
        self.assertIsNotNone(traslado_query)
        self.assertEqual(traslado_query.origen, "Ciudad A")
        self.assertEqual(traslado_query.destino, "Ciudad B")
        self.assertEqual(traslado_query.tramo, "1")

    def test_eliminar_traslado(self):
        """Prueba la eliminación de un traslado"""
        traslado = Traslado(
            id=self.actividad.id,
            origen="Ciudad A",
            destino="Ciudad B",
            tramo="1"
        )
        db.session.add(traslado)
        db.session.commit()

        db.session.delete(traslado)
        db.session.commit()

        traslado_query = Traslado.query.get(self.actividad.id)
        self.assertIsNone(traslado_query)
