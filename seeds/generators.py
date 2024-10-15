"""Generadores de datos

Usamos Flask-Seeder para ejecutar los "seeds".
Usamos Faker para crear más generadores de los que incluye Flask-Seeder.

"""
import random
from faker import Faker
from faker.providers import address, internet, python
from flask_seeder.generator import Generator

faker = Faker('es_AR')
faker.add_provider(address)
faker.add_provider(internet)
faker.add_provider(python)


class Legajo(Generator):
    def generate(self):
        return 'EMP-' + str(faker.unique.pyint(min_value=0, max_value=999999))


class FirstName(Generator):
    def generate(self):
        return faker.first_name()


class LastName(Generator):
    def generate(self):
        return faker.last_name()


class Rol(Generator):
    tipos = ['autorizante', 'consulta', 'gestion', 'gestion']

    def generate(self):
        return random.choice(self.tipos)


class Establecimiento(Generator):
    tipos = ['H', 'CS', 'PS']

    def generate(self):
        return random.choice(self.tipos) + ' ' + faker.name()


class Ubicacion(Generator):
    def generate(self):
        return faker.street_address() + ', Neuquén'
