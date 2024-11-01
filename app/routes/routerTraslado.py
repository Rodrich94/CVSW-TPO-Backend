from flask import Blueprint,jsonify
from ..controllers.traslado_controller import crear_traslado,get_traslado,eliminar_traslado, get_traslados
from ..models import Traslado  


router_traslado = Blueprint('traslado', __name__)

@router_traslado.route('/traslado', methods=['POST'])
def agregar_traslado():
    return crear_traslado()


@router_traslado.route('/traslado/<int:id>', methods=['DELETE'])
def borrar_traslado(id):
    return eliminar_traslado(id)



@router_traslado.route('/traslados', methods=['GET'])
def obtener_traslados():
    return get_traslados()

# Obtener traslado por id
@router_traslado.route('/traslado/<int:id>', methods=['GET'])
def obtener_traslado(id):
    return get_traslado(id)