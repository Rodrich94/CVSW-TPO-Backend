from flask import request, jsonify
from ..models import Traslado, ActividadExtraordinaria, Licencia  # Importa los modelos necesarios
from ..utils import verificar_fechas
from .. import db  

def crear_traslado():
    data = request.get_json()
    
    # Extraer datos del JSON
    origen = data.get('origen')
    destino = data.get('destino')
    tramo = data.get('tramo')
    fecha_inicio = data.get('fecha_inicio')  # Asegúrate de que estos campos estén en el JSON
    fecha_fin = data.get('fecha_fin')
    empleado_id = data.get('empleado_id')  # Suponiendo que estás recibiendo el ID del empleado

    # Validar fechas
    validacion, mensaje = verificar_fechas(fecha_inicio, fecha_fin, empleado_id)
    if not validacion:
        return jsonify({"error": mensaje}), 400

    # Crear nuevo traslado
    nuevo_traslado = Traslado(origen=origen, destino=destino, tramo=tramo)
    
    db.session.add(nuevo_traslado)
    db.session.commit()

    return jsonify({"message": "Traslado creado exitosamente", "traslado": str(nuevo_traslado)}), 201