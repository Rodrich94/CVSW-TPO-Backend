from flask import Blueprint
from app.controllers.guardia_controller import obtener_guardias, modificar_guardia

router_guardia = Blueprint('guardias', __name__)

@router_guardia.route('/guardias', methods=['GET'])
def listar_guardias():
    return obtener_guardias()

@router_guardia.route('/guardia', methods=['PUT'])
def cambio_empleado_en_guardia():
    return modificar_guardia()
