from flask import Blueprint, jsonify
from ..models import Establecimiento  

# Definir el Blueprint
router_establecimiento = Blueprint('router_establecimiento', __name__)

# Definir la ruta para obtener servicios
@router_establecimiento.route('/establecimientos', methods=['GET'])
def obtener_establecimientos():
    establecimientos = Establecimiento.query.all()
    resultado = [
        {
            "id": establecimiento.id,
            "nombre": establecimiento.nombre,
            "ubicacion": establecimiento.ubicacion
        } for establecimiento in establecimientos
    ]
    return jsonify(resultado), 200


@router_establecimiento.route('/establecimientos/<int:establecimiento_id>/servicios', methods=['GET'])
def obtener_servicios_establecimiento(establecimiento_id):
    establecimiento = Establecimiento.query.get(establecimiento_id)
    if not establecimiento:
        return jsonify({"error": "Establecimiento no encontrado"}), 404

    servicios = [
        {
            "id": servicio.id,
            "nombre": servicio.nombre
        } for servicio in establecimiento.servicios
    ]
    return jsonify(servicios), 200