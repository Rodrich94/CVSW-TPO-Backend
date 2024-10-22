from app.models import ActividadExtraordinaria, Licencia, Empleado,DiagramaMensual
from datetime import datetime
from flask import jsonify

def verificar_fechas(fecha_inicio, fecha_fin, empleado_legajo):
    # Validar si hay superposición de fechas con actividades extraordinarias
    actividades = ActividadExtraordinaria.query.filter(
        ActividadExtraordinaria.legajo_empleado == empleado_legajo,
        ActividadExtraordinaria.fecha_ini <= fecha_fin,
        ActividadExtraordinaria.fecha_fin >= fecha_inicio
    ).all()

    if actividades:
        return False, "Superposición con otra actividad."

    # lógica para validar la licencia
    licencias = Licencia.query.filter(
        Licencia.legajo_empleado == empleado_legajo,
        Licencia.fecha_desde <= fecha_fin,
        Licencia.fecha_hasta >= fecha_inicio
    ).all()

    if licencias:
        return False, "Superposición con licencia."

    return True, "Validación exitosa."


# Verificar si el empleado existe
def verificar_EmpleadoID(empleado_id):
    empleado = Empleado.query.filter_by(legajo=empleado_id).first()
    if empleado:
        return True
    


def convertir_fechas(fecha_ini_str, fecha_fin_str):
    #Convierte cadenas de fechas en formato 'YYYY-MM-DD' a objetos de fecha.
    try:
        fecha_ini = datetime.strptime(fecha_ini_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        return fecha_ini, fecha_fin
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"}), 400
    

def validar_fechas(fecha_ini, fecha_fin):
    """
    Verifica si la fecha de inicio es mayor que la fecha de fin.
    """
    if fecha_ini > fecha_fin:
        return jsonify({"error": "La fecha de inicio no puede ser mayor a la fecha de fin"}), 400
    return None

def verificar_diagrama_existente(fecha_ini, fecha_fin):
    """
    Verifica si ya existe un diagrama en el rango de fechas especificado.
    """
    existe_diagrama = DiagramaMensual.query.filter(
        DiagramaMensual.fecha_ini <= fecha_fin,
        DiagramaMensual.fecha_fin >= fecha_ini
    ).first()

    if existe_diagrama:
        return jsonify({"error": "Ya existe un diagrama en el rango de fechas especificado"}), 400
    return None

def buscar_actividades(fecha_ini, fecha_fin, servicio_id):
    """
    Busca actividades extraordinarias dentro del rango de fechas.
    """
    actividades = ActividadExtraordinaria.query.filter(
        ActividadExtraordinaria.fecha_ini.between(fecha_ini, fecha_fin),
        ActividadExtraordinaria.servicio_id == servicio_id
    ).all()

    if not actividades:
        return jsonify({"error": "No se encontraron actividades extraordinarias en el rango de fechas"}), 404

    return actividades