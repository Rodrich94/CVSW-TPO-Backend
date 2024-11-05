from flask import Blueprint
from app.controllers.guardia_controller import obtener_guardias, crear_guardias, obtener_guardias_por_servicio_tipo, modificar_empleado_guardia

router_guardia = Blueprint('guardias', __name__)

@router_guardia.route('/guardias', methods=['GET'])
def listar_guardias():
    return obtener_guardias()

@router_guardia.route('/guardia/empleado', methods=['POST'])
def agregar_guardias():
    return crear_guardias()

@router_guardia.route('/guardias/servicio-tipo', methods=['GET'])
def listar_guardias_por_servicio_tipo():
    return obtener_guardias_por_servicio_tipo()

@router_guardia.route('/guardia/cambiar-empleado/<int:id_guardia>', methods=['PUT'])
def cambio_empleado_en_guardia(id_guardia):
    return modificar_empleado_guardia(id_guardia)