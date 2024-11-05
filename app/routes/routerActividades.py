from flask import Blueprint
from app.controllers.actividades_controller import obtener_actividades, obtener_resumen_actividades_por_servicio


router_actividades = Blueprint('actividades', __name__)


@router_actividades.route('/actividades/empleado/<string:legajo_empleado>', methods=['GET'])
def get_actividades(legajo_empleado):
    return obtener_actividades(legajo_empleado)

@router_actividades.route('/actividades/servicio/<int:id_servicio>', methods=['GET'])
def get_resumen_actividades_por_servicio(id_servicio):
    return obtener_resumen_actividades_por_servicio(id_servicio)