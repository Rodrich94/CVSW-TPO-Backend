from flask import request, jsonify
from ..models import DiagramaMensual, ActividadExtraordinaria, ActividadDiagrama, db
from ..utils.utils import validar_datos_diagrama,buscar_actividades
from datetime import datetime
from dateutil.relativedelta import relativedelta


def ajustar_fechas_mes_diferido(mes, anio):
    try:

        # Establecer la fecha de inicio al 16 del mes y año especificados
        fecha_ini = datetime(anio, mes, 16)
        
        # Calcular la fecha de fin como el 15 del mes siguiente
        fecha_fin = (fecha_ini + relativedelta(months=1)).replace(day=15)
        return fecha_ini, fecha_fin
    except ValueError:
        return jsonify({"error": "Formato de mes y año no es valido, deben ser enteros y positivos"}), 400    
        

# Controlador para crear un nuevo diagrama
def crear_diagrama():
    data = request.get_json()
 
    # Extraer el mes y año del JSON
    mes = data.get('mes')
    anio = data.get('anio')
    servicio_id = data.get('servicio_id')

    # Ajustar fechas de inicio y fin al ciclo de 16 a 15 para el mes y año especificados
    fecha_ini, fecha_fin = ajustar_fechas_mes_diferido(mes, anio)

    # Validar los datos recibidos
    validacion, mensaje = validar_datos_diagrama(data,fecha_ini,fecha_fin)
    if not validacion:
        return jsonify({"error": mensaje}), 400

    # Buscar las actividades extraordinarias dentro del rango de fechas ajustado
    actividades = buscar_actividades(fecha_ini, fecha_fin, servicio_id)
    if isinstance(actividades, tuple):
        return actividades  # Retorna el error si no hay actividades

    # Crear el nuevo diagrama mensual
    nuevo_diagrama = DiagramaMensual(
        fecha_ini=fecha_ini,
        fecha_fin=fecha_fin,
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
            'servicio': diagrama.servicio.nombre,
            'actividades_extraordinarias': [
                {
                    'id': actividad.id, 
                    'fecha_ini': actividad.fecha_ini.strftime('%Y-%m-%d'), 
                    'fecha_fin': actividad.fecha_fin.strftime('%Y-%m-%d'),
                    'estado': actividad.estado,
                    'nombre_empleado': actividad.empleado.nombre,
                    'apellido_empleado': actividad.empleado.apellido,
                    'legajo_empleado': actividad.empleado.legajo,
                    'tipo_actividad': 'guardia' if actividad.guardias else 'traslado' if actividad.traslado else 'desconocido'
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
        'servicio': diagrama.servicio.nombre,
        'actividades_extraordinarias': [
            {'id': actividad.id,
             'tipo_actividad': 'guardia' if actividad.guardias else 'traslado' if actividad.traslado else 'desconocido', 
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


    if fecha_inicio:
        query = query.filter(DiagramaMensual.fecha_ini >= fecha_inicio)

    if fecha_fin:
        query = query.filter(DiagramaMensual.fecha_fin <= fecha_fin)

 
    if estado:
        query = query.filter(DiagramaMensual.estado == estado)

    if servicio_id:
        query = query.filter(DiagramaMensual.servicio_id == servicio_id)

    diagramas = query.all()

    resultado = []
    for diagrama in diagramas:
        resultado.append({
            'id': diagrama.id,
            'fecha_ini': diagrama.fecha_ini.strftime('%Y-%m-%d'),
            'fecha_fin': diagrama.fecha_fin.strftime('%Y-%m-%d'),
            'servicio_id': diagrama.servicio_id,
            'actividades_extraordinarias': [
                {'id': actividad.id, 
                 'fecha_ini': actividad.fecha_ini.strftime('%Y-%m-%d'), 
                 'fecha_fin': actividad.fecha_fin.strftime('%Y-%m-%d'),
                 'estado': actividad.estado} for actividad in diagrama.actividades_extraordinarias
            ]
        })

    return jsonify(resultado), 200