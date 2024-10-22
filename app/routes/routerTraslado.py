from flask import Blueprint,jsonify
from ..controllers.traslado_controller import crear_traslado,get_traslado,eliminar_traslado
from ..models import Traslado  


router_traslado = Blueprint('traslado', __name__)

@router_traslado.route('/traslado', methods=['POST'])
def agregar_traslado():
    return crear_traslado()


@router_traslado.route('/traslado/<int:id>', methods=['DELETE'])
def borrar_traslado(id):
    return eliminar_traslado(id)



@router_traslado.route('/traslados', methods=['GET'])
def get_traslados():
    traslados = Traslado.query.all()
    return jsonify([{
        'id': traslado.id,
        'origen': traslado.origen,       
        'destino': traslado.destino,      
        'tramo': traslado.tramo
    } for traslado in traslados])

# Obtener traslado por id
@router_traslado.route('/traslado/<int:id>', methods=['GET'])
def obtener_traslado(id):
    return get_traslado(id)