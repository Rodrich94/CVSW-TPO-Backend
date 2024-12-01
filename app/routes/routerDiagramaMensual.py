from flask import Blueprint
from ..controllers.diagrama_controller import crear_diagrama, obtener_diagramas,eliminar_diagrama,obtener_diagrama_por_id,obtener_diagramas_filtrados

# Crear un Blueprint para las rutas de DiagramaMensual
router_diagrama = Blueprint('diagrama', __name__)

# Ruta para crear un nuevo diagrama
@router_diagrama.route('/diagrama', methods=['POST'])
def agregar_diagrama():
    return crear_diagrama()

# Ruta para obtener todos los diagramas
@router_diagrama.route('/diagramas', methods=['GET'])
def ver_diagramas():
    return obtener_diagramas()


# Ruta para eliminar un diagrama
@router_diagrama.route('/diagrama/<int:diagrama_id>', methods=['DELETE'])
def elimina_diagrama(diagrama_id):
    return eliminar_diagrama(diagrama_id)


# Ruta para obtener un diagrama
@router_diagrama.route('/diagrama/<int:diagrama_id>', methods=['GET'])
def obtener_diagrama(diagrama_id):
    return obtener_diagrama_por_id(diagrama_id)


# Ruta para obtener diagramas filtrados
@router_diagrama.route('/diagramas/filtrados', methods=['GET'])
def obtener_diagramas_filtro():
    return obtener_diagramas_filtrados()