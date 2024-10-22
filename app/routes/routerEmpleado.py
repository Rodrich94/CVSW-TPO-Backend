from flask import Blueprint, jsonify
from ..models import Empleado  

# Definir el Blueprint
router_empleado = Blueprint('router_empleado', __name__)

# Definir la ruta para obtener empleados
@router_empleado.route('/empleados', methods=['GET'])
def get_empleados():
    empleados = Empleado.query.all()
    return jsonify([{
        'legajo': empleado.legajo,
        'nombre': empleado.nombre,
        'apellido': empleado.apellido,
        'rol': empleado.rol,
        'servicio': empleado.servicio.nombre
    } for empleado in empleados])
