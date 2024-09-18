from . import db

# Modelo Establecimiento
class Establecimiento(db.Model):
    __tablename__ = 'establecimientos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    ubicacion = db.Column(db.String(30), nullable=False)
    
    # Relación con el modelo Servicio (1 a Muchos)
    servicios = db.relationship('Servicio', backref='establecimiento', lazy=True)

    def __repr__(self):
        return f"<Establecimiento {self.nombre}>"

# Modelo Servicio
class Servicio(db.Model):
    __tablename__ = 'servicios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    
    # Foreign Key a la tabla Establecimiento
    establecimiento_id = db.Column(db.Integer, db.ForeignKey('establecimientos.id'), nullable=False)

    # Relación con el modelo Empleado (1 Servicio -> Muchos Empleados)
    empleados = db.relationship('Empleado', backref='servicio', lazy=True)

    def __repr__(self):
        return f"<Servicio {self.nombre}>"

# Modelo Empleado
class Empleado(db.Model):
    __tablename__ = 'empleados'
    
    legajo = db.Column(db.String(20), primary_key=True)
    nombre = db.Column(db.String(40), nullable=False)
    apellido = db.Column(db.String(40), nullable=False)
    rol = db.Column(db.String(40), nullable=False)

    # Foreign Key a la tabla Servicio
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)

    def __repr__(self):
        return f"<Empleado {self.legajo} - {self.nombre} {self.apellido}>"


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
        return f"<Licencia {self.fecha_desde} - {self.fecha_hasta}>"
    
# Modelo Cupo Mensual
class CupoMensual(db.Model):
    __tablename__ = 'cupos_mensuales'

    id = db.Column(db.Integer, primary_key=True)
    fecha_ini = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    total = db.Column(db.Double, nullable=False)
    remanente = db.Column(db.Double, nullable=False)

    # Foreign Key a la tabla Servicio
    id_servicio = db.Column(db.Integer,
                            db.ForeignKey('servicios.id'),
                            nullable=False)
    # Foreign Key a la tabla Empleado (autorizante)
    legajo_autorizante = db.Column(db.String(20),
                                   db.ForeignKey('empleados.legajo'),
                                   nullable=False)

    def __repr__(self):
        return f"<CupoMensual {self.fecha_desde} - {self.fecha_hasta}>"

# Modelo DiagramaMensual
class DiagramaMensual(db.Model):
    __tablename__ = 'diagramas_mensuales'

    id = db.Column(db.Integer, primary_key=True)
    fecha_ini = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), nullable=False)

    # Foreign Key a la tabla Servicio
    id_servicio = db.Column(db.Integer,
                            db.ForeignKey('servicios.id'),
                            nullable=False)

    def __repr__(self):
        return f"<DiagramaMensual {self.fecha_ini} - {self.fecha_fin}>"