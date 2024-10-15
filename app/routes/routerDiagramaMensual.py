from flask import Blueprint
from ..controllers.diagrama_controller import crear_diagrama, obtener_diagramas

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
