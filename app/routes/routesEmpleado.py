from flask import Blueprint, jsonify
from ..models import Empleado  # Ajusta la ruta para importar los modelos

main = Blueprint('main', __name__)

@main.route('/empleados', methods=['GET'])
def get_empleados():
    empleados = Empleado.query.all()
    return jsonify([{
        'legajo': empleado.legajo,
        'nombre': empleado.nombre,
        'apellido': empleado.apellido,
        'rol': empleado.rol,
        'servicio': empleado.servicio.nombre
    } for empleado in empleados])
