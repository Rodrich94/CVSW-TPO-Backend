from flask import request, jsonify
from ..models import DiagramaMensual, ActividadExtraordinaria, ActividadDiagrama, db
from ..utils.utils import convertir_fechas, validar_fechas, verificar_diagrama_existente, buscar_actividades

# Controlador para crear un nuevo diagrama
def crear_diagrama():
    data = request.get_json()
    
    # Extraer los datos del JSON
    fecha_ini_str = data.get('fecha_ini')
    fecha_fin_str = data.get('fecha_fin')
    estado = data.get('estado')
    servicio_id = data.get('servicio_id')
    
    # Convertir las fechas de cadena a objetos de fecha
    resultado = convertir_fechas(fecha_ini_str, fecha_fin_str)
    if isinstance(resultado, tuple):
        fecha_ini, fecha_fin = resultado
    else:
        return resultado
    
    # Validar que las fechas sean correctas
    validacion_fecha = validar_fechas(fecha_ini, fecha_fin)
    if validacion_fecha:
        return validacion_fecha

    # Verificar si ya existe un diagrama en el rango de fechas
    verificacion_diagrama = verificar_diagrama_existente(fecha_ini, fecha_fin)
    if verificacion_diagrama:
        return verificacion_diagrama

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
            'servicio_id': diagrama.servicio_id,
            'actividades_extraordinarias': [
                {'id': actividad.id, 
                 'fecha_ini': actividad.fecha_ini.strftime('%Y-%m-%d'), 
                 'fecha_fin': actividad.fecha_fin.strftime('%Y-%m-%d'),
                 'estado': actividad.estado} for actividad in diagrama.actividades_extraordinarias
            ]
        })
    return jsonify(resultado), 200
