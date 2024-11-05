from flask import Blueprint
from app.controllers.actividades_controller import obtener_actividades


router_actividades = Blueprint('actividades', __name__)


@router_actividades.route('/actividades/empleado/<string:legajo_empleado>', methods=['GET'])
def get_actividades(legajo_empleado):
    return obtener_actividades(legajo_empleado)
