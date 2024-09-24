from . import db
import click
from flask.cli import with_appcontext

# Modelo Establecimiento
class Establecimiento(db.Model):
    __tablename__ = 'establecimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    ubicacion = db.Column(db.String(30), nullable=False)
    
    # Relación con el modelo Servicio (1 a Muchos)
    servicios = db.relationship('Servicio', backref='establecimiento', lazy=True)

    def __repr__(self):
        return f"<Establecimiento {self.id} - {self.nombre} - {self.ubicacion}>"

# Modelo Servicio
class Servicio(db.Model):
    __tablename__ = 'servicios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    
    # Foreign Key a la tabla Establecimiento
    establecimiento_id = db.Column(db.Integer, db.ForeignKey('establecimientos.id'), nullable=False)

    # Relación con el modelo Empleado (1 Servicio -> Muchos Empleados)
    empleados = db.relationship('Empleado', backref='servicio', lazy=True)

    # Relación inversa de ActividadesExtraordinarias sobre un Servicio
    actividades_extraordinarias = db.relationship('ActividadExtraordinaria', backref='servicio')

    def __repr__(self):
        return f"<Servicio {self.id} - {self.nombre}>"

# Modelo Empleado
class Empleado(db.Model):
    __tablename__ = 'empleados'
    
    legajo = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(40), nullable=False)
    apellido = db.Column(db.String(40), nullable=False)
    rol = db.Column(db.String(40), nullable=False)

    # Foreign Key a la tabla Servicio
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)

    # Relación inversa de ActividadesExtraordinarias de un Empleado
    actividades_extraordinarias = db.relationship('ActividadExtraordinaria', backref='empleado')

    def __repr__(self):
        return f"<Empleado {self.legajo} - {self.nombre} - {self.apellido} - {self.rol}>"


class Licencia(db.Model):
    __tablename__ = 'licencias'

    id = db.Column(db.Integer, primary_key=True)
    fecha_desde = db.Column(db.Date, nullable=False)
    fecha_hasta = db.Column(db.Date, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)

    # Foreign Key a la tabla Empleado (se toma licencia)
    legajo_empleado = db.Column(db.String(20),
                                db.ForeignKey('empleados.legajo'),
                                nullable=False)
    # Foreign Key a la tabla Empleado (autorizante)
    legajo_autorizante = db.Column(db.String(20),
                                   db.ForeignKey('empleados.legajo'),
                                   nullable=False)

    # Relación con Empleado (se toma licencia)
    empleado = db.relationship('Empleado', foreign_keys=[legajo_empleado])

    # Relación con Empleado (autorizante)
    autorizante = db.relationship('Empleado', foreign_keys=[legajo_autorizante])

    def __repr__(self):
        return f"<Licencia {self.id} - {self.fecha_desde} - {self.fecha_hasta} - {self.tipo}>"
    
# Modelo Cupo Mensual
class CupoMensual(db.Model):
    __tablename__ = 'cupos_mensuales'

    id = db.Column(db.Integer, primary_key=True)
    fecha_ini = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    total = db.Column(db.Double, nullable=False)
    remanente = db.Column(db.Double, nullable=False)

    # Foreign Key a la tabla Servicio
    servicio_id = db.Column(db.Integer,
                            db.ForeignKey('servicios.id'),
                            nullable=False)
    # Foreign Key a la tabla Empleado (autorizante)
    legajo_autorizante = db.Column(db.String(20),
                                   db.ForeignKey('empleados.legajo'),
                                   nullable=False)

    guardias = db.relationship('Guardia', backref='guardia')

    def __repr__(self):
        return f"<CupoMensual {self.id} - {self.fecha_ini} - {self.fecha_fin} - {self.total} - {self.remanente}>"

# Modelo DiagramaMensual
class DiagramaMensual(db.Model):
    __tablename__ = 'diagramas_mensuales'

    id = db.Column(db.Integer, primary_key=True)
    fecha_ini = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    # Foreign Key a la tabla Servicio
    servicio_id = db.Column(db.Integer,
                            db.ForeignKey('servicios.id'),
                            nullable=False)

    # Relación inversa de ActividadesExtraordinarias de un Empleado
    actividades_extraordinarias = db.relationship('ActividadExtraordinaria', backref='diagrama_mensual')

    def __repr__(self):
        return f"<DiagramaMensual {self.id} - {self.fecha_ini} - {self.fecha_fin} - {self.estado}>"

# Modelo ActividadExtraordinaria
class ActividadExtraordinaria(db.Model):
    __tablename__ = 'actividades_extraordinarias'
    
    id = db.Column(db.Integer, primary_key=True)
    fecha_ini = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    # Foreign Key a la tabla Servicio
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)

    # Foreign Key a la tabla Empleado
    legajo_empleado = db.Column(db.String(20), db.ForeignKey('empleados.legajo'), nullable=False)

    # Foreign Key a la tabla DiagramaMensual
    diagrama_mensual_id = db.Column(db.Integer, db.ForeignKey('diagramas_mensuales.id'), nullable=False)    

    def __repr__(self):
        return f"<ActividadExtraordinaria {self.id} - {self.fecha_ini} - {self.fecha_fin} - {self.estado}>"
    
# Modelo Guardia
class Guardia(db.Model):
    __tablename__ = 'guardias'
    
    id = db.Column(db.Integer, db.ForeignKey('actividades_extraordinarias.id'), nullable=False, primary_key=True)
    duracion = db.Column(db.String(20), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)   

    # Foreign Key a la tabla CupoMensual
    cupo_mensual_id = db.Column(db.Integer, db.ForeignKey('cupos_mensuales.id'), nullable=False)

    def __repr__(self):
        return f"<Guardia {self.id} - {self.duracion} - {self.tipo} - {self.cupo_mensual_id}>"
    
# Modelo Traslado
class Traslado(db.Model):
    __tablename__ = 'traslados'
    
    id = db.Column(db.Integer, db.ForeignKey('actividades_extraordinarias.id'), nullable=False, primary_key=True)
    origen = db.Column(db.String(40), nullable=False)
    destino = db.Column(db.String(40), nullable=False)   
    tramo = db.Column(db.Integer, nullable=False)   

    def __repr__(self):
        return f"<Traslado {self.id} - {self.origen} - {self.destino} - {self.tramo}>"

@click.command(name='init')
@with_appcontext
def init_db():
    db.drop_all()
    db.create_all()

@click.command(name='populate')
@with_appcontext
def populate_db():
    db.session.add(Establecimiento(nombre='unEstablecimiento', ubicacion='Neuquén'))

    db.session.add(Servicio(nombre='unServicio', establecimiento_id='1'))

    db.session.add(
        Empleado(
            legajo="E001",
            nombre='Roberto', 
            apellido='Bolaños',
            rol='Enfermero',
            servicio_id='1'
        )
    )

    db.session.commit()