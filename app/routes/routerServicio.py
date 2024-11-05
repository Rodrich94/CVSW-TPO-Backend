from flask import Blueprint, jsonify
from ..models import Servicio,Establecimiento  

# Definir el Blueprint
router_servicio = Blueprint('router_servicio', __name__)

# Definir la ruta para obtener servicios
@router_servicio.route('/servicios', methods=['GET'])
def get_servicios():
    servicios = Servicio.query.all()
    return jsonify([{
        'id': servicio.id,
        'nombre': servicio.nombre,
        'establecimiento': servicio.establecimiento.nombre
    } for servicio in servicios])



@router_servicio.route('/servicios/<int:servicio_id>/empleados', methods=['GET'])
def obtener_empleados_servicio(servicio_id):
    servicio = Servicio.query.get(servicio_id)
    if not servicio:
        return jsonify({"error": "Servicio no encontrado"}), 404

    empleados = [
        {
            "legajo": empleado.legajo,
            "nombre": empleado.nombre,
            "apellido": empleado.apellido,
            "rol": empleado.rol
        } for empleado in servicio.empleados
    ]
    return jsonify(empleados), 200

# Definir la ruta para obtener servicios por id de establecimiento
@router_servicio.route('/servicios/establecimiento/<int:establecimiento_id>', methods=['GET'])
def obtener_servicios_por_establecimiento(establecimiento_id):
    establecimiento = Establecimiento.query.get(establecimiento_id)
    if not establecimiento:
        return jsonify({"error": "Establecimiento no encontrado"}), 404

    servicios = [
        {
            'id': servicio.id,
            'nombre': servicio.nombre,
        } for servicio in establecimiento.servicios
    ]
    return jsonify(servicios), 200