from flask import Blueprint, jsonify
from ..models import Servicio  

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
