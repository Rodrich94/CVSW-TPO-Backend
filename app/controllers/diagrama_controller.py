from flask import request, jsonify
from ..models import DiagramaMensual, ActividadExtraordinaria, ActividadDiagrama, db
from datetime import datetime

# Controlador para crear un nuevo diagrama
def crear_diagrama():
    data = request.get_json()
    
    # Extraer los datos del JSON
    fecha_ini_str = data.get('fecha_ini')
    fecha_fin_str = data.get('fecha_fin')
    estado = data.get('estado')
    servicio_id = data.get('servicio_id')
    
    # Convertir las fechas de cadena a objetos de fecha
    try:
        fecha_ini = datetime.strptime(fecha_ini_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"}), 400
    
    # Validar que las fechas sean correctas
    if fecha_ini > fecha_fin:
        return jsonify({"error": "La fecha de inicio no puede ser mayor a la fecha de fin"}), 400

    # Buscar las actividades extraordinarias dentro del rango de fechas
    actividades = ActividadExtraordinaria.query.filter(
        ActividadExtraordinaria.fecha_ini.between(fecha_ini, fecha_fin),
        ActividadExtraordinaria.servicio_id == servicio_id
    ).all()
    
    if not actividades:
        return jsonify({"error": "No se encontraron actividades extraordinarias en el rango de fechas"}), 404

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
