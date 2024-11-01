import random
from flask_seeder import Seeder, Faker
from app.models import Empleado, Establecimiento, Servicio, Traslado, ActividadExtraordinaria,Licencia,CupoMensual
from seeds import generators
from datetime import datetime, timedelta

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
        for establecimiento in faker.create(5):
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

        for empleado in faker.create(50):
            empleado.servicio_id = random.choice(ids_servicios)
            print("Agregando Empleado: %s" % empleado)
            self.db.session.add(empleado)



class Traslados(Seeder):
    def run(self):
        # IDs de empleados y servicios
        ids_empleados = self.db.session.query(Empleado.legajo).all()
        ids_empleados = [row[0] for row in ids_empleados]
        ids_servicios = self.db.session.query(Servicio.id).all()
        ids_servicios = [row[0] for row in ids_servicios]

        # Establecer la fecha de inicio en enero
        fecha_inicio_base = datetime(year=2024, month=1, day=1)

        for i in range(30):  # Cambia el número según necesites
            # Calcular la fecha de inicio y fin
            fecha_inicio = fecha_inicio_base + timedelta(days=i * 30)  # Aproximación de 30 días por mes
            fecha_fin = fecha_inicio + timedelta(days=1)  # La fecha de fin es un día después

            # Obtener el legajo del empleado aleatorio
            legajo_empleado = random.choice(ids_empleados)


            actividad_existente = self.db.session.query(ActividadExtraordinaria).filter(
                ActividadExtraordinaria.legajo_empleado == legajo_empleado,
                ActividadExtraordinaria.fecha_ini <= fecha_fin,
                ActividadExtraordinaria.fecha_fin >= fecha_inicio
            ).first()

            # Verificar si hay una licencia vigente para el empleado
            licencia_vigente = self.db.session.query(Licencia).filter(
                Licencia.legajo_empleado == legajo_empleado,
                Licencia.fecha_desde <= fecha_fin,
                Licencia.fecha_hasta >= fecha_inicio
            ).first()

            # Solo añadir el traslado si no hay conflictos
            if not actividad_existente and not licencia_vigente:
                nueva_actividad = ActividadExtraordinaria(
                    fecha_ini=fecha_inicio.strftime('%Y-%m-%d'),
                    fecha_fin=fecha_fin.strftime('%Y-%m-%d'),
                    estado="Pendiente",
                    servicio_id=random.choice(ids_servicios),
                    legajo_empleado=legajo_empleado
                )
                self.db.session.add(nueva_actividad)
                self.db.session.flush()  # Para obtener el ID de la actividad
                origen_ubicacion = generators.Ubicacion().generate()
                destino_ubicacion = generators.Ubicacion().generate()
                # Ahora crear el traslado
                nuevo_traslado = Traslado(
                    id=nueva_actividad.id,  # El traslado comparte el ID de la actividad
                    origen=origen_ubicacion,
                    destino=destino_ubicacion,
                    tramo=random.choice(['1', '2', '3'])  # Asegúrate de que estos valores son válidos
                )
                print("Agregando Traslado: %s" % nuevo_traslado)
                self.db.session.add(nuevo_traslado)

        # Guardar todos los cambios al final
        self.db.session.commit()




# Crear licencias random para la BD
class Licencias(Seeder):
    def run(self):
        faker = Faker(
            cls=Licencia,
            init={
                'fecha_desde': generators.Fecha(),
                'fecha_hasta': generators.Fecha(),
                'tipo': generators.TipoLicencia(),
            }
        )

        # IDs de empleados
        ids = self.db.session.query(Empleado.legajo).all()
        ids_empleados = [row[0] for row in ids]

        for licencia in faker.create(20):
            licencia.legajo_empleado = random.choice(ids_empleados)
            licencia.legajo_autorizante = random.choice(ids_empleados)
            print("Agregando Licencia: %s" % licencia)
            self.db.session.add(licencia)


# Crear cupos mensuales random para la BD
class CuposMensuales(Seeder):
    def run(self):
        faker = Faker(
            cls=CupoMensual,
            init={
                'fecha_ini': generators.Fecha(),
                'fecha_fin': generators.Fecha(),
                'total': generators.CupoTotal(),
                'remanente': generators.CupoRemanente(),
            }
        )

        # IDs de servicios
        ids_servicios = [servicio.id for servicio in self.db.session.query(Servicio.id).all()]
        ids_autorizantes = [empleado.legajo for empleado in self.db.session.query(Empleado.legajo).all()]

        for cupo_mensual in faker.create(50):
            cupo_mensual.servicio_id = random.choice(ids_servicios)
            cupo_mensual.legajo_autorizante = random.choice(ids_autorizantes)
            print("Agregando Cupo Mensual: %s" % cupo_mensual)
            self.db.session.add(cupo_mensual)




# Ejecutar todos los seeders
class SeederAll(Seeder):
    def run(self):
        self.db.create_all()
        # Llama al método run() de cada seeder
        Establecimientos(self.db).run()
        Servicios(self.db).run()
        Empleados(self.db).run()
        CuposMensuales(self.db).run()
        Licencias(self.db).run()
        Traslados(self.db).run()
