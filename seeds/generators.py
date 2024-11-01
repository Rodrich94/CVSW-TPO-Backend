"""Generadores de datos

Usamos Flask-Seeder para ejecutar los "seeds".
Usamos Faker para crear más generadores de los que incluye Flask-Seeder.

"""
import random
from faker import Faker
from faker.providers import address, internet, python
from flask_seeder.generator import Generator
from datetime import datetime
faker = Faker('es_AR')
faker.add_provider(address)
faker.add_provider(internet)
faker.add_provider(python)


class Legajo(Generator):
    def generate(self):
        return 'E' + str(faker.unique.pyint(min_value=0, max_value=999999))


class FirstName(Generator):
    def generate(self):
        return faker.first_name()


class LastName(Generator):
    def generate(self):
        return faker.last_name()


class Rol(Generator):
    tipos = ['Gestion', 'Autorizante']

    def generate(self):
        return random.choice(self.tipos)


class Establecimiento(Generator):
    tipos = ['H', 'CS', 'PS']

    def generate(self):
        return random.choice(self.tipos) + ' ' + faker.name()


class Ubicacion(Generator):
    def generate(self):
        return faker.street_address() + ', Neuquén'



class Fecha(Generator):
    def generate(self):
        # Generar una fecha aleatoria entre el 1 de enero de 2023 y el 31 de diciembre de 2024
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2024, 12, 31)
        random_date = faker.date_between(start_date=start_date, end_date=end_date)
        # Convertir a string en el formato adecuado (YYYY-MM-DD)
        return random_date.strftime('%Y-%m-%d')


class TipoLicencia(Generator):
    tipos = ['vacaciones', 'enfermedad', 'paternidad', 'maternidad', 'otros']

    def generate(self):
        return random.choice(self.tipos)


class CupoTotal(Generator):
    def generate(self):
        return round(random.uniform(500, 1500), 2)


class CupoRemanente(Generator):
    def generate(self):
        return round(random.uniform(0, 500), 2)


class Duracion(Generator):
    duraciones = ['media jornada', 'jornada completa', 'turno nocturno']

    def generate(self):
        return random.choice(self.duraciones)


class TipoGuardia(Generator):
    tipos = ['presencial', 'remota']

    def generate(self):
        return random.choice(self.tipos)


class Direccion(Generator):
    def generate(self):
        return faker.street_address() + ', Neuquén'


class Tramo(Generator):
    tramos = ['1', '2', '3']

    def generate(self):
        return random.choice(self.tramos)
