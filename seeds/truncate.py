from flask_seeder import Seeder, Faker
from app.models import Empleado, Establecimiento, Servicio
from seeds import generators


# Trunca la BD completa
class Truncar(Seeder):
    def run(self):
        self.db.drop_all()
        self.db.create_all()
