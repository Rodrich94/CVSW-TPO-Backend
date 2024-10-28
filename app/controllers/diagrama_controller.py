from flask import request, jsonify
from ..models import DiagramaMensual, ActividadExtraordinaria, ActividadDiagrama, db
from ..utils.utils import convertir_fechas, validar_datos_diagrama,buscar_actividades
# Controlador para crear un nuevo diagrama
def crear_diagrama():
    data = request.get_json()
    # Validar los datos recibidos
    validacion, mensaje = validar_datos_diagrama(data)
    if not validacion:
        return jsonify({"error": mensaje}), 400    

    # Extraer los datos del JSON
    fecha_ini_str = data.get('fecha_inicio')
    fecha_fin_str = data.get('fecha_fin')
    estado = data.get('estado')
    servicio_id = data.get('servicio_id')
    
    # Convertir las fechas de cadena a objetos de fecha
    resultado = convertir_fechas(fecha_ini_str, fecha_fin_str)
    if isinstance(resultado, tuple):
        fecha_ini, fecha_fin = resultado
    else:
        return resultado  
    

    # Buscar las actividades extraordinarias dentro del rango de fechas
    actividades = buscar_actividades(fecha_ini, fecha_fin, servicio_id)
    if isinstance(actividades, tuple):
        return actividades  # Retorna el error si no hay actividades

    # Crear el nuevo diagrama mensual
    nuevo_diagrama = DiagramaMensual(
        fecha_ini=fecha_ini,
        fecha_fin=fecha_fin,
        estado=estado,
        servicio_id=servicio_id
    )
    
    # Agregar el diagrama
    db.session.add(nuevo_diagrama)
    db.session.flush()  # Para obtener el ID del nuevo diagrama

    # Asociar las actividades encontradas al nuevo diagrama
    for actividad in actividades:
        actividad_diagrama = ActividadDiagrama(
            actividad_id=actividad.id,
            diagrama_id=nuevo_diagrama.id
        )
        db.session.add(actividad_diagrama)

    # Confirmar la transacción
    db.session.commit()
    
    return jsonify({"message": "Diagrama creado exitosamente", "diagrama_id": nuevo_diagrama.id}), 201

# Controlador para obtener todos los diagramas
def obtener_diagramas():
    diagramas = DiagramaMensual.query.all()
    resultado = []
    for diagrama in diagramas:
        resultado.append({
            'id': diagrama.id,
            'fecha_ini': diagrama.fecha_ini.strftime('%Y-%m-%d'),
            'fecha_fin': diagrama.fecha_fin.strftime('%Y-%m-%d'),
            'estado': diagrama.estado,
            'servicio': diagrama.servicio.nombre,
            'actividades_extraordinarias': [
                {'id': actividad.id, 
                 'fecha_ini': actividad.fecha_ini.strftime('%Y-%m-%d'), 
                 'fecha_fin': actividad.fecha_fin.strftime('%Y-%m-%d'),
                 'estado': actividad.estado,
                 'nombre_empleado': actividad.empleado.nombre,
                 'apellido_empleado': actividad.empleado.apellido,
                 'legajo_empleado': actividad.empleado.legajo
                 } for actividad in diagrama.actividades_extraordinarias
            ]
        })
    return jsonify(resultado), 200


# Controlador para eliminar un diagrama
def eliminar_diagrama(diagrama_id):
    diagrama = DiagramaMensual.query.get(diagrama_id)
    
    if not diagrama:
        return jsonify({"error": "Diagrama no encontrado"}), 404

    # Eliminar el diagrama y sus asociaciones
    db.session.delete(diagrama)
    db.session.commit()
    
    return jsonify({"message": "Diagrama eliminado exitosamente"}), 200


# Controlador para obtener un diagrama específico
def obtener_diagrama_por_id(diagrama_id):
    diagrama = DiagramaMensual.query.get(diagrama_id)

    if not diagrama:
        return jsonify({"error": "Diagrama no encontrado"}), 404

    resultado = {
        'id': diagrama.id,
        'fecha_ini': diagrama.fecha_ini.strftime('%Y-%m-%d'),
        'fecha_fin': diagrama.fecha_fin.strftime('%Y-%m-%d'),
        'estado': diagrama.estado,
        'servicio': diagrama.servicio.nombre,
        'actividades_extraordinarias': [
            {'id': actividad.id, 
             'fecha_ini': actividad.fecha_ini.strftime('%Y-%m-%d'), 
             'fecha_fin': actividad.fecha_fin.strftime('%Y-%m-%d'),
             'estado': actividad.estado,
             'nombre_empleado': actividad.empleado.nombre,
             'apellido_empleado': actividad.empleado.apellido,
             'legajo_empleado': actividad.empleado.legajo} for actividad in diagrama.actividades_extraordinarias
        ]
    }

    return jsonify(resultado), 200




# Controlador para obtener diagramas filtrados
def obtener_diagramas_filtrados():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    estado = request.args.get('estado')
    servicio_id = request.args.get('servicio_id')

    query = DiagramaMensual.query

    # Filtrar por fecha de inicio
    if fecha_inicio:
        query = query.filter(DiagramaMensual.fecha_ini >= fecha_inicio)

    # Filtrar por fecha de fin
    if fecha_fin:
        query = query.filter(DiagramaMensual.fecha_fin <= fecha_fin)

    # Filtrar por estado
    if estado:
        query = query.filter(DiagramaMensual.estado == estado)

    # Filtrar por servicio_id
    if servicio_id:
        query = query.filter(DiagramaMensual.servicio_id == servicio_id)

    diagramas = query.all()

    resultado = []
    for diagrama in diagramas:
        resultado.append({
            'id': diagrama.id,
            'fecha_ini': diagrama.fecha_ini.strftime('%Y-%m-%d'),
            'fecha_fin': diagrama.fecha_fin.strftime('%Y-%m-%d'),
            'estado': diagrama.estado,
            'servicio_id': diagrama.servicio_id,
            'actividades_extraordinarias': [
                {'id': actividad.id, 
                 'fecha_ini': actividad.fecha_ini.strftime('%Y-%m-%d'), 
                 'fecha_fin': actividad.fecha_fin.strftime('%Y-%m-%d'),
                 'estado': actividad.estado} for actividad in diagrama.actividades_extraordinarias
            ]
        })

    return jsonify(resultado), 200