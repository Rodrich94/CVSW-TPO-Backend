from app.models import ActividadExtraordinaria, Licencia, Empleado, CupoMensual, DiagramaMensual, Servicio
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import jsonify

# Función para verificar si las fechas tienen el formato correcto y si son válidas
def verificar_fechas(fecha_inicio, fecha_fin, empleado_legajo):
    formato_fecha = "%Y-%m-%d"
    
    try:
        # Verificar formato de fecha
        fecha_inicio_dt = datetime.strptime(fecha_inicio, formato_fecha)
        fecha_fin_dt = datetime.strptime(fecha_fin, formato_fecha)
        
        # Verificar que fecha_inicio < fecha_fin
        if fecha_inicio_dt > fecha_fin_dt:
            return False, "La fecha de inicio no puede ser mayor que la fecha de fin."

        # Validar si hay superposición de fechas con actividades extraordinarias
        actividades_existentes = ActividadExtraordinaria.query.filter(
            ActividadExtraordinaria.legajo_empleado == empleado_legajo,
            ActividadExtraordinaria.fecha_ini <= fecha_fin,
            ActividadExtraordinaria.fecha_fin >= fecha_inicio
        ).all()
        
        if actividades_existentes:
            return False, f"El empleado ya tiene una actividad extraordinaria entre {fecha_inicio} y {fecha_fin}."
        

        # lógica para validar la licencia
        licencias = Licencia.query.filter(
            Licencia.legajo_empleado == empleado_legajo,
            Licencia.fecha_desde <= fecha_fin,
            Licencia.fecha_hasta >= fecha_inicio
        ).all()

        if licencias:
            return False, "Superposición con licencia."

        return True, "Fechas válidas"
    
    except ValueError:
        return False, "Formato de fecha no válido. El formato debe ser 'YYYY-MM-DD'."




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


def verificar_empleado(legajo_empleado):
    """
    Verifica si existe el empelado por su legajo.
    """
    empleado = Empleado.query.filter_by(legajo=legajo_empleado).first()
    if empleado:
        return True, "Validación exitosa."
    else:
        return False, f"El empleado con legajo {legajo_empleado} no existe."


def verificar_servicio(servicio_id):
    """
    Verifica si existe el servicio por su ID.
    """
    servicio = Servicio.query.filter_by(id=servicio_id).first()
    if servicio:
        return True, "Validación exitosa."
    else:
        return False, f"El servicio #{servicio_id} no existe."


def validar_tipo_guardia(tipo):
    """
    Verifica si el tipo de guardia es correcto.
    """
    tipo = tipo.lower()
    if tipo == "activa" or tipo == "pasiva":
        return True, "Validación exitosa."
    else:
        return False, f"El tipo de guardias ({tipo}) es incorrecto."


def validar_fechas_guardia(fecha_ini, fecha_fin, periodo):
    """
    Verifica que las fecha de inicio y fin de una guardia sean correctas.
    """
    try:
        fecha_min = datetime.strptime(periodo[0], "%Y-%m-%d").date()
        fecha_max = datetime.strptime(periodo[1], "%Y-%m-%d").date()
        fin_periodo = fecha_min + relativedelta(months=1)
        if fecha_min.day != 16 or fecha_max.day != 15 or fecha_max.month != fin_periodo.month:
            return False, "El periodo es incorrecto."

        fecha_ini = datetime.strptime(fecha_ini, "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        fecha_dif = fecha_fin - fecha_ini
        if fecha_dif.days > 1:
            return False, "Las fechas de guardia difieren en más de un día."
        elif fecha_dif.days < 0:
            return False, "La fecha de fin debe ser mayor a la de inicio."
        elif fecha_ini < fecha_min or fecha_fin > fecha_max:
            return False, "Las fechas de guardia no corresponden al periodo."
        else:
            return True, "Validación exitosa."
    except ValueError:
        return False, "Formato de fecha de guardia inválido."


def validar_duracion_guardia(duracion):
    """
    Verifica que la duración de guardia sea correcta (12 o 24 horas).
    """
    horas_duracion = int(duracion)
    if horas_duracion == 12 or horas_duracion == 24:
        return True, "Validación exitosa."
    else:
        return False, f"La duración de guardia ({duracion} hs) es incorrecta."


def verificar_cantidad_guardias(tipo, cantidad):
    """
    Verifica que la cantidad de guardias no exceda los límites.
    """
    if tipo == "activa" and cantidad > 10:
        return False, "Guardias activas excedidas por empleado."
    elif tipo == "pasiva" and cantidad > 15:
        return False, "Guardias pasivas excedidas por empleado."
    else:
        return True, "Validación exitosa."
    # TODO: verificar también que no excendan con las que ya existan en la DB


def verificar_cupo_mensual(servicio_id, fecha_ini, fecha_fin, cantidad):
    """
    Verificar si existe cupo mensual válido de guardias para un servicio.
    """
    cupo_mensual = CupoMensual.query.filter(
        CupoMensual.servicio_id == servicio_id,
        CupoMensual.fecha_ini <= fecha_ini,
        CupoMensual.fecha_fin >= fecha_fin
    ).first()  # TODO: ver el caso en que existan más de un cupo válidos

    if cupo_mensual:
        if cupo_mensual.remanente >= cantidad:
            return True, "Validación exitosa."
        else:
            return False, "Cupo mensual excedido."

    return False, "No existe un cupo mensual para el servicio."
