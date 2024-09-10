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
