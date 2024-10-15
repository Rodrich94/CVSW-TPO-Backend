from flask import request, Blueprint
from app.controllers.guardia_controller import obtener_guardias, modificar_guardia

guardias_blueprint = Blueprint('guardias', __name__)

@guardias_blueprint.route('/', methods=['GET'])
def listar_guardias():
    return obtener_guardias()

@guardias_blueprint.route('/', methods=['PUT'])
def cambio_empleado_en_guardia():
    return modificar_guardia()
