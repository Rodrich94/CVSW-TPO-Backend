import random
from flask_seeder import Seeder, Faker
from app.models import Empleado, Establecimiento, Servicio
from seeds import generators


# Crear establecimientos random para la BD
class Establecimientos(Seeder):
    def run(self):
        faker = Faker(
            cls=Establecimiento,
            init={
                'nombre': generators.Establecimiento(),
                'ubicacion': generators.Ubicacion()
            }
        )
        for establecimiento in faker.create(200):
            print("Agregando Establecimiento: %s" % establecimiento)
            self.db.session.add(establecimiento)


# Crear servicios random para la BD
class Servicios(Seeder):
    def run(self):
        # IDs de establecimientos
        ids = self.db.session.query(Establecimiento.id).all()
        ids_establecimientos = [row[0] for row in ids]
        servicios = ['Atención al Público', 'Clínica Médica', 'Enfermería',
                     'Medicina General', 'Cardiología', 'Odontología',
                     'Pediatría', 'Obstetricia', 'Radiología', 'Laboratorio']
        for id_establecimiento in ids_establecimientos:
            for nombre_servicio in servicios:
                servicio = Servicio(
                    nombre=nombre_servicio,
                    establecimiento_id=id_establecimiento
                )
                print("Agregando Servicio: %s" % servicio)
                self.db.session.add(servicio)


# Crear empleados random para la BD
class Empleados(Seeder):
    def run(self):
        faker = Faker(
            cls=Empleado,
            init={
                'legajo': generators.Legajo(),
                'nombre': generators.FirstName(),
                'apellido': generators.LastName(),
                'rol': generators.Rol(),
            }
        )
        # IDs de servicios
        ids = self.db.session.query(Servicio.id).all()
        ids_servicios = [row[0] for row in ids]

        for empleado in faker.create(500):
            empleado.servicio_id = random.choice(ids_servicios)
            print("Agregando Empleado: %s" % empleado)
            self.db.session.add(empleado)
