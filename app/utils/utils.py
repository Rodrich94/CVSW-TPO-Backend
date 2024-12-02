from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import case, func
from flask import jsonify
from app.models import ActividadExtraordinaria, Guardia, Traslado, Licencia, Empleado, CupoMensual, DiagramaMensual, Servicio, Establecimiento
from .. import db
import re 

# Función para verificar si las fechas tienen el formato correcto y si son válidas
def verificar_fechas(fecha_inicio, fecha_fin, empleado_legajo):
    formato_fecha = "%Y-%m-%d"
    
    try:
        # Verificar formato de fecha
        fecha_inicio_dt = datetime.strptime(fecha_inicio, formato_fecha)
        fecha_fin_dt = datetime.strptime(fecha_fin, formato_fecha)
        
        # Verificar que fecha_inicio < fecha_fin
        if not fecha_inicio_dt < fecha_fin_dt:
            return False, "La fecha de inicio debe ser menor a la de fin"

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


# Función para validar los campos de entrada de un traslado
def validar_datos_traslado(data):
    # Verificar que los campos requeridos existan
    campos_requeridos = ['origen', 'destino', 'tramo', 'fecha_inicio', 'fecha_fin', 'empleado_id', 'servicio_id']
    
    for campo in campos_requeridos:
        if campo not in data:
            return False, f"El campo '{campo}' es requerido."
        
    if 'servicio_id' in data:
        servicio_id = int(data['servicio_id'])
        if servicio_id < 0:
            return False, f"El 'servicio_id' debe ser un número positivo"

    # Verificar que el empleado tenga el formato correcto y exista
    validacion_empleado, mensaje_empleado = verificar_EmpleadoID(data['empleado_id'])
    if not validacion_empleado:
        return False, mensaje_empleado
    
    # Verificar el formato y rango de las fechas
    validacion_fechas, mensaje_fechas = verificar_fechas(data['fecha_inicio'], data['fecha_fin'], data['empleado_id'])
    if not validacion_fechas:
        return False, mensaje_fechas

    # Verificar que el tramo sea válido
    validacion_tramo, mensaje_tramo = verificar_tramo(data['tramo'])
    if not validacion_tramo:
        return False, mensaje_tramo

    # Validar que el servicio_id corresponde al empleado_id
    if not verificar_servicio_empleado(data['empleado_id'], data['servicio_id']):
        return False, f"El 'servicio_id' {data['servicio_id']} no corresponde al 'empleado_id' {data['empleado_id']}."


    return True, "Datos válidos"


def validar_datos_diagrama(data,fecha_inicio,fecha_fin):
    # Verificar que los campos requeridos existan
    campos_requeridos = ['mes', 'anio', 'servicio_id']
  
    for campo in campos_requeridos:
        if campo not in data:
            return False, f"El campo '{campo}' es requerido."

    # Verificar que las fechas sean correctas
    
    validacion_fechas, mensaje_fecha = validar_mes_anio(data['mes'],data['anio'])
    if not validacion_fechas:
        return False, mensaje_fecha
    
    # Verificar que no exista diagrama en fechas
    validacion_fechas, mensaje_diagrama = verificar_diagrama_existente(fecha_inicio, fecha_fin)
    if not validacion_fechas:
        return False, mensaje_diagrama

    # Retornar éxito si todas las validaciones pasan
    return True, "Datos del diagrama válidos"

# Función para verificar si el servicio_id corresponde al empleado_id
def verificar_servicio_empleado(empleado_id, servicio_id):
    # Aquí debes consultar tu base de datos para obtener el servicio_id del empleado
    empleado = db.session.query(Empleado).filter(Empleado.legajo == empleado_id).first()
    
    if empleado is None:
        return False  # El empleado no existe

    # Comparar el servicio_id del empleado con el proporcionado
    return empleado.servicio_id == servicio_id


def verificar_EmpleadoID(empleado_id):
    # Verificar si el formato es correcto
    if not re.match(r'^E\d{1,6}$', empleado_id):
        return False, f"El legajo del empleado '{empleado_id}' no es válido. Debe tener el formato 'E000001'. (7 digitos)"

    # Verificar si el empleado existe
    empleado = Empleado.query.filter_by(legajo=empleado_id).first()
    if empleado is None:
        return False, f"El legajo tiene formato válido '{empleado_id}' pero el empleado no existe."

    return True, f"El legajo '{empleado_id}' es válido y el empleado existe."


def verificar_tramo(tramo):
    tramos_validos = ['1', '2', '3']
    if tramo not in tramos_validos:
        return False, f"El tramo '{tramo}' no es válido. Debe ser 1 (100km - 180km), 2(181km - 360km) o 3 (mas de 360km)."
    
    return True, f"El tramo '{tramo}' es válido."



def convertir_fechas(fecha_ini_str, fecha_fin_str):
    #Convierte cadenas de fechas en formato 'YYYY-MM-DD' a objetos de fecha.
    try:
        fecha_ini = datetime.strptime(fecha_ini_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        return fecha_ini, fecha_fin
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido"}), 400
    

def validar_mes_anio(mes, anio):
    """
    Verifica que el mes esté entre 1 y 12 y que el año sea positivo.
    """
    try:
        mes = int(mes)
        anio = int(anio)

        if mes < 1 or mes > 12:
            return False, "El mes debe estar entre 1 y 12"
        
        if anio < 0:
            return False, "El año debe ser un valor positivo"

        return True, "El mes y el año son válidos"
    
    except ValueError:
        return False, "El mes y el año deben ser enteros positivos"

    
def verificar_diagrama_existente(fecha_ini, fecha_fin):
    """
    Verifica si ya existe un diagrama en el rango de fechas especificado.
    """
    existe_diagrama = DiagramaMensual.query.filter(
        DiagramaMensual.fecha_ini <= fecha_fin,
        DiagramaMensual.fecha_fin >= fecha_ini
    ).first()

    if existe_diagrama:
        return False, "Ya existe un diagrama en el rango de fechas especificado"
    return True, "No existe ningún diagrama en el rango de fechas"

def buscar_actividades(fecha_ini, fecha_fin, servicio_id):
    """
    Busca actividades extraordinarias dentro del rango de fechas.
    """
    actividades = ActividadExtraordinaria.query.filter(
        ActividadExtraordinaria.fecha_ini >= fecha_ini,
        ActividadExtraordinaria.fecha_ini <= fecha_fin,
        ActividadExtraordinaria.servicio_id == servicio_id
    ).all()
    print("Actividad",actividades)
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


def validar_cantidad_guardias(tipo, cantidad):
    tipo = tipo.lower()
    """
    Valida que la cantidad de guardias no exceda los límites.
    """
    if tipo == "activa" and cantidad > 10:
        return False, f"Guardias activas excedidas ({cantidad}/10) por empleado."
    elif tipo == "pasiva" and cantidad > 15:
        return False, f"Guardias pasivas excedidas ({cantidad}/15) por empleado."
    else:
        return True, "Validación exitosa."


def verificar_cantidad_guardias(legajo_empleado, tipo, fecha_min, fecha_max, cantidad):
    """
    Verifica que las guardias no excendan los límites por empleado y por periodo:
    - 10 activas;
    - 15 pasivas.
    """
    guardias_empleado = (
        db.session.query(
            ActividadExtraordinaria.legajo_empleado,
            func.sum(Guardia.duracion).label('suma_guardias')
        ).join(Guardia, ActividadExtraordinaria.id == Guardia.id).filter(
            ActividadExtraordinaria.legajo_empleado == legajo_empleado,
            ActividadExtraordinaria.fecha_ini >= fecha_min,
            ActividadExtraordinaria.fecha_fin <= fecha_max,
            Guardia.tipo == tipo
        ).group_by(ActividadExtraordinaria.legajo_empleado).first()
    )

    if guardias_empleado:
        cantidad += float(guardias_empleado[1]) / 24

    return validar_cantidad_guardias(tipo, cantidad)


def verificar_cupo_mensual(servicio_id, fecha_ini, fecha_fin, cantidad):
    """
    Verificar si existe cupo mensual válido de guardias para un servicio.
    """
    cupo_mensual = CupoMensual.query.filter(
        CupoMensual.servicio_id == servicio_id,
        CupoMensual.fecha_ini <= fecha_ini,
        CupoMensual.fecha_fin >= fecha_fin,
        CupoMensual.remanente >= cantidad
    ).first()

    if cupo_mensual:
        return cupo_mensual, "Validación exitosa."
    else:
        return False, "No existe un cupo mensual válido para el servicio."


def validar_rango_fechas(fecha_desde, fecha_hasta):
    """
    Valida un rango de fechas desde y hasta, con formato YYYY-MM-DD.
    """
    try:
        desde = datetime.strptime(fecha_desde, "%Y-%m-%d").date()
        hasta = datetime.strptime(fecha_hasta, "%Y-%m-%d").date()
        if desde > hasta:
            return False, "La fecha desde no puede ser mayor a la fecha hasta."
        else:
            return True, "Validación exitosa."
    except ValueError:
        return False, "Formato de fecha inválido."


def obtener_actividades_empleado(legajo_empleado, fecha_desde, fecha_hasta):
    """
    Obtiene las actividades de un empleado para un rango de fechas [desde; hasta].
    """
    actividades = []
    resultado = (
        db.session.query(
            ActividadExtraordinaria,
            Guardia,
            Traslado,
            Servicio,
            Establecimiento,
            Empleado,
            case((Traslado.id == None, 'Guardia'), else_='Traslado')
        ).join(
            Guardia,
            Guardia.id == ActividadExtraordinaria.id,
            isouter=True
        ).join(
            Traslado,
            Traslado.id == ActividadExtraordinaria.id,
            isouter=True
        ).join(
            Servicio,
            Servicio.id == ActividadExtraordinaria.servicio_id
        ).join(
            Establecimiento,
            Establecimiento.id == Servicio.establecimiento_id
        ).join(
            Empleado,
            Empleado.legajo == ActividadExtraordinaria.legajo_empleado
        ).filter(
            ActividadExtraordinaria.legajo_empleado == legajo_empleado,
            ActividadExtraordinaria.fecha_ini >= fecha_desde,
            ActividadExtraordinaria.fecha_fin <= fecha_hasta
        )
    ).all()

    for tupla in resultado:
        actividad, guardia, traslado, servicio, establecimiento, empleado, tipo = tupla

        if guardia is not None:
            detalle_actividad = {
                'duracion': guardia.duracion,
                'tipo': guardia.tipo,
            }
        else:
            detalle_actividad = {
                'origen': traslado.origen,
                'destino': traslado.destino,
                'tramo': traslado.tramo,
            }

        actividades.append({
            'legajo': empleado.legajo,
            'nombre': empleado.nombre,
            'apellido': empleado.apellido,
            'id': actividad.id,
            'id_servicio': servicio.id,
            'nombre_servicio': servicio.nombre,
            'nombre_establecimiento': establecimiento.nombre,
            'ubicacion_establecimiento': establecimiento.ubicacion,
            'fecha_ini': actividad.fecha_ini.strftime("%Y-%m-%d"),
            'fecha_fin': actividad.fecha_fin.strftime("%Y-%m-%d"),
            'estado': actividad.estado,
            'tipo': tipo,
            'detalle': detalle_actividad,
        })

    return actividades


def validar_fecha_modificar_empleado_guardia(fecha):
    """
    Verifica que la fecha de guardia ingresada sea correcta.
    """
    try:
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        #if fecha > datetime.now().date():
        #    return False, "La fecha no puede ser mayor a la actual."
        #else:
        #    return True, "Validación exitosa."
        return True, "Validación exitosa."
    except ValueError:
        return False, "Formato de fecha de guardia inválido."
    

def obtener_periodo_fecha(fecha):
    """
    Dada una fecha previamente validada, obtiene el rango de fechas inicio y fin a partir de la misma.
    """
    try:
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date()
        if (16 <= fecha.day <= 31):
            inicio_periodo = fecha.replace(day=16)
            fin_periodo = (fecha + relativedelta(months=1)).replace(day=15)
        elif (1 <= fecha.day <= 15):
            inicio_periodo = (fecha - relativedelta(months=1)).replace(day=16)
            fin_periodo = fecha.replace(day=15)
        else: 
            return False, "Formato de fecha incorrecto."
    except ValueError:
        return False, "Formato de fecha incorrecto."
    
    periodo_fecha = [inicio_periodo, fin_periodo]
    return periodo_fecha, "Operacion exitosa."


def verificar_rol_empleados(legajo_empleado_actual, legajo_nuevo_empleado):
    """
    Verifica que ambos empleados posean el mismo rol.
    """
    empleado_actual = Empleado.query.filter_by(legajo=legajo_empleado_actual).first()
    empleado_nuevo = Empleado.query.filter_by(legajo=legajo_nuevo_empleado).first()
    
    if empleado_actual.rol != empleado_nuevo.rol:
        return False, "Los roles de ambos empleados deben coincidir."
    else:
        return True, "Validación exitosa."


def verificar_guardia(guardia_id):
    """
    Verifica si la guardia existe mediante su ID.
    """
    guardia = Guardia.query.get(guardia_id)
    if guardia is None:
        return False, f"La guardia #{guardia_id} no existe."
    elif guardia.actividad_extraordinaria.estado == "Realizada":
        return False, "No se puede modificar una guardia con estado 'Realizada'."
    else:
        return True, "Validación de guardia exitosa."
    

def obtener_resumen_actividades_empleado(servicio_id, fecha_desde, fecha_hasta):
    """
    Obtiene el resumen de actividades por servicio en un rango de fechas.
    """
    resultados_resumen_servicio = []

    # Obtener las actividades extraordinarias dentro del rango de fechas y servicio
    actividades_extraordinarias = ActividadExtraordinaria.query.filter(
        ActividadExtraordinaria.servicio_id == servicio_id,
        ActividadExtraordinaria.fecha_ini >= fecha_desde,
        ActividadExtraordinaria.fecha_fin <= fecha_hasta
    ).all()

    # Inicializar un diccionario para almacenar el resumen por empleado
    resumen_empleados = {}

    for actividad in actividades_extraordinarias:
        legajo_empleado = actividad.legajo_empleado

        if legajo_empleado not in resumen_empleados:
            empleado = Empleado.query.filter_by(legajo=legajo_empleado).first()
            resumen_empleados[legajo_empleado] = {
                'nombre': empleado.nombre,
                'apellido': empleado.apellido,
                'dias_licencia': 0,
                'cantidad_guardias': 0,
                'cantidad_traslados': 0
            }

            # Contabilizar días de licencia
            licencias = Licencia.query.filter(
                Licencia.legajo_empleado == legajo_empleado,
                Licencia.fecha_desde >= fecha_desde,
                Licencia.fecha_hasta <= fecha_hasta
            ).all()

            for licencia in licencias:
                resumen_empleados[legajo_empleado]['dias_licencia'] += (licencia.fecha_hasta - licencia.fecha_desde).days + 1

        # Contabilizar guardias y traslados
        if actividad.guardias:
            resumen_empleados[legajo_empleado]['cantidad_guardias'] += 1
        elif actividad.traslado:
            resumen_empleados[legajo_empleado]['cantidad_traslados'] += 1

    # Agregar el resumen al resultado final
    for legajo_empleado, datos in resumen_empleados.items():
        resultados_resumen_servicio.append({
        'legajo_empleado': legajo_empleado,
        'nombre': datos['nombre'],
        'apellido': datos['apellido'],
        'dias_licencia': datos['dias_licencia'],
        'cantidad_guardias': datos['cantidad_guardias'],
        'cantidad_traslados': datos['cantidad_traslados']
        })

    return resultados_resumen_servicio
