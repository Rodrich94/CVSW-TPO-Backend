from flask import request, jsonify
from ..models import Traslado, ActividadExtraordinaria, Licencia  # Importa los modelos necesarios
from ..utils.utils import verificar_fechas
from .. import db  
from sqlalchemy.orm import joinedload 
def crear_traslado():
    data = request.get_json()
    
    # Extraer datos del JSON
    origen = data.get('origen')
    destino = data.get('destino')
    tramo = data.get('tramo')
    fecha_inicio = data.get('fecha_inicio')  
    fecha_fin = data.get('fecha_fin')
    empleado_id = data.get('empleado_id')  # Suponiendo que estás recibiendo el ID del empleado
    servicio_id = data.get('servicio_id')  # Servicio al que pertenece la actividad
    
    # Validar fechas
    validacion, mensaje = verificar_fechas(fecha_inicio, fecha_fin, empleado_id)
    if not validacion:
        return jsonify({"error": mensaje}), 400

    # Crear la actividad extraordinaria primero (que incluye las fechas)
    nueva_actividad = ActividadExtraordinaria(
        fecha_ini=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="Pendiente",  # Puedes cambiar esto según lo que necesites
        servicio_id=servicio_id,
        legajo_empleado=empleado_id
    )
    
    db.session.add(nueva_actividad)
    db.session.flush()  # Guarda la actividad en la base de datos pero no confirma la transacción
    
    # Ahora que la actividad tiene un ID, puedes asociar el traslado con la actividad
    nuevo_traslado = Traslado(
        id=nueva_actividad.id,  # El traslado comparte el ID de la actividad extraordinaria
        origen=origen,
        destino=destino,
        tramo=tramo
    )
    
    db.session.add(nuevo_traslado)
    db.session.commit()  # Confirma la transacción para ambas inserciones

    return jsonify({"message": "Traslado creado exitosamente", "traslado": str(nuevo_traslado)}), 201


# Función para obtener los datos de un traslado y su actividad extraordinaria
def get_traslado(id):
    # Consultar el traslado con la actividad extraordinaria asociada
    traslado = db.session.query(Traslado).join(ActividadExtraordinaria).filter(Traslado.id == id).first()

    if traslado:
        # Crear la respuesta con los datos del traslado y de la actividad extraordinaria asociada
        response = {
            'traslado_id': traslado.id,
            'origen': traslado.origen,
            'destino': traslado.destino,
            'tramo': traslado.tramo,
            'id': {
                'fecha_ini': traslado.actividad.fecha_ini,
                'fecha_fin': traslado.actividad.fecha_fin,
                'estado': traslado.actividad.estado,
                'servicio_id': traslado.actividad.servicio_id
            }
        }
        return jsonify(response), 200
    else:
        return jsonify({'error': 'Traslado no encontrado'}), 404