from flask import Blueprint, jsonify
from ..models import Empleado,Servicio  

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


@router_empleado.route('/empleado/<string:legajo>', methods=['GET'])
def get_empleado(legajo):
    empleado = Empleado.query.get(legajo)
    if not empleado:
        return jsonify({
            'error': f'No existe el empleado ({legajo}).'
        }), 404

    return jsonify({
        'legajo': empleado.legajo,
        'nombre': empleado.nombre,
        'apellido': empleado.apellido,
        'rol': empleado.rol,
        'servicio': empleado.servicio.nombre
    }), 200
