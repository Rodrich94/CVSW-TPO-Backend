from flask import request, jsonify
from ..models import Traslado, ActividadExtraordinaria, Empleado 
from ..utils.utils import validar_datos_traslado
from .. import db  
from sqlalchemy.orm import joinedload 


def crear_traslado():
    data = request.get_json()
    

    # Validar los datos recibidos
    validacion, mensaje = validar_datos_traslado(data)
    if not validacion:
        return jsonify({"error": mensaje}), 400


    # Extraer datos del JSON
    origen = data.get('origen')
    destino = data.get('destino')
    tramo = data.get('tramo')
    fecha_inicio = data.get('fecha_inicio')  
    fecha_fin = data.get('fecha_fin')
    empleado_id = data.get('empleado_id')  
    servicio_id = data.get('servicio_id')  
    
    
    # Crear la actividad extraordinaria primero (que incluye las fechas)
    nueva_actividad = ActividadExtraordinaria(
        fecha_ini=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="Pendiente",  
        servicio_id=servicio_id,
        legajo_empleado=empleado_id
    )
    
    db.session.add(nueva_actividad)
    db.session.flush()  # Guarda la actividad en la base de datos pero no confirma la transacción
    
    # Ahora que la actividad tiene un ID, se asocia el traslado con la actividad
    nuevo_traslado = Traslado(
        id=nueva_actividad.id,  # El traslado comparte el ID de la actividad extraordinaria
        origen=origen,
        destino=destino,
        tramo=tramo
    )
    
    db.session.add(nuevo_traslado)
    db.session.commit() 

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
            'actividad': {
                'fecha_ini': traslado.actividad.fecha_ini,
                'fecha_fin': traslado.actividad.fecha_fin,
                'estado': traslado.actividad.estado,
                'servicio_id': traslado.actividad.servicio.nombre,
                'nombre_empleado': traslado.actividad.empleado.nombre,
                'apellido_empleado': traslado.actividad.empleado.apellido,
                'legajo_empleado': traslado.actividad.empleado.legajo
            }
        }
        return jsonify(response), 200
    else:
        return jsonify({'error': 'Traslado no encontrado'}), 404


def eliminar_traslado(id):
    # Buscar el traslado por su ID
    traslado = db.session.query(Traslado).filter_by(id=id).first()

    if traslado is None:
        return jsonify({"error": "Traslado no encontrado"}), 404

    # Buscar la actividad extraordinaria asociada al traslado
    actividad = db.session.query(ActividadExtraordinaria).filter_by(id=traslado.id).first()

    # Eliminar el traslado y la actividad
    db.session.delete(traslado)
    if actividad:
        db.session.delete(actividad)
    
    db.session.commit()

    return jsonify({"message": f"Traslado con ID {id} eliminado exitosamente"}), 200


def get_traslados():
    traslados = Traslado.query.all()
    return jsonify([{
        'id': traslado.id,
        'origen': traslado.origen,       
        'destino': traslado.destino,      
        'tramo': traslado.tramo,
        'actividad': {
                'servicio_id': traslado.actividad.servicio.nombre,
                'nombre_empleado': traslado.actividad.empleado.nombre,
                'apellido_empleado': traslado.actividad.empleado.apellido,
                'legajo_empleado': traslado.actividad.empleado.legajo
            }
    } for traslado in traslados])