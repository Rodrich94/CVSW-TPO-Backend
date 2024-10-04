from flask import Blueprint
from app.controllers.traslado_controller import crear_traslado

router_traslado = Blueprint('traslado', __name__)

@router_traslado.route('/traslado', methods=['POST'])
def agregar_traslado():
    return crear_traslado()
