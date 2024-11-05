from flask import request, jsonify
from ..models import Guardia, ActividadExtraordinaria
from .. import db
from ..utils.utils import (verificar_empleado, verificar_fechas, verificar_cupo_mensual, verificar_servicio, validar_tipo_guardia, validar_fechas_guardia, validar_duracion_guardia, verificar_cantidad_guardias,
                           validar_fecha_modificar_empleado_guardia, verificar_EmpleadoID, obtener_periodo_fecha, verificar_guardia, verificar_rol_empleados)

def obtener_guardias():
    guardias = Guardia.query.all()
    return jsonify([{
        'id': guardia.id,
        'fechaInicio': guardia.actividad_extraordinaria.fecha_ini,
        'fechaFin': guardia.actividad_extraordinaria.fecha_fin,
        'estado': guardia.actividad_extraordinaria.estado,
        'servicio': guardia.actividad_extraordinaria.servicio.nombre,
        'legajoEmpleado': guardia.actividad_extraordinaria.empleado.legajo,
        'duracion': guardia.duracion,
        'tipo': guardia.tipo,
    } for guardia in guardias])


def crear_guardias():
    """
    Realiza alta de guardias por empleado.
    """
    data = request.get_json()
    tipo = data.get('tipo')
    periodo = data.get('periodo')
    servicio_id = data.get('servicio_id')
    legajo_empleado = data.get('legajo_empleado')
    guardias = data.get('guardias')

    # Verificar tipo de guardias
    tipo_valido, error = validar_tipo_guardia(tipo)
    if not tipo_valido:
        return jsonify({'error': error}), 400

    # Verificar servicio
    servicio_valido, error = verificar_servicio(servicio_id)
    if not servicio_valido:
        return jsonify({'error': error}), 400

    # Verificar empleado
    empleado_valido, error = verificar_empleado(legajo_empleado)
    if not empleado_valido:
        return jsonify({'error': error}), 400

    # Datos para verificar cupo mensual y cantidad de guardias
    fecha_min = periodo[0]
    fecha_max = periodo[1]
    cantidad_guardias = 0.0

    # Verificar guardias
    for guardia in guardias:
        fecha_ini = guardia.get('fecha_ini')
        fecha_fin = guardia.get('fecha_fin')
        duracion = guardia.get('duracion')

        # Validar fechas de guardia
        fechas_validas, error = validar_fechas_guardia(fecha_ini, fecha_fin, periodo)
        if not fechas_validas:
            return jsonify({'error': error}), 400

        # Validar duracion de guardia
        duracion_valida, error = validar_duracion_guardia(duracion)
        if not duracion_valida:
            return jsonify({'error': error}), 400

        # Verificar superposición con licencias y actividades
        fechas_verificadas, error = verificar_fechas(fecha_ini, fecha_fin, legajo_empleado)
        if not fechas_verificadas:
            return jsonify({'error': error}), 400

        # Sumar guardias de acuerdo a su duración
        cantidad_guardias += int(duracion) / 24

    # Verificar cantidad de guardias
    cantidad_valida, error = verificar_cantidad_guardias(legajo_empleado, tipo, fecha_min, fecha_max, cantidad_guardias)
    if not cantidad_valida:
        return jsonify({'error': error}), 400

    # Verificar cupo mensual
    cupo_valido, error = verificar_cupo_mensual(
        servicio_id,
        fecha_min,
        fecha_max,
        cantidad_guardias
    )
    if not cupo_valido:
        return jsonify({'error': error}), 400

    # Crear las guardias
    for guardia in guardias:
        fecha_ini = guardia.get('fecha_ini')
        fecha_fin = guardia.get('fecha_fin')
        duracion = guardia.get('duracion')

        nueva_actividad = ActividadExtraordinaria(
            fecha_ini=fecha_ini,
            fecha_fin=fecha_fin,
            estado='Pendiente',
            servicio_id=servicio_id,
            legajo_empleado=legajo_empleado
        )
        db.session.add(nueva_actividad)
        db.session.flush()

        nueva_guardia = Guardia(
            id=nueva_actividad.id,
            duracion=duracion,
            tipo=tipo,
            cupo_mensual_id=cupo_valido.id
        )
        db.session.add(nueva_guardia)
        db.session.flush()

    # Actualizar el cupo mensual
    cupo_valido.remanente -= cantidad_guardias
    db.session.commit()

    return jsonify({
        'mensaje': 'Guardias creadas con éxito.',
        'cantidad_guardias': cantidad_guardias
    }), 201


def obtener_guardias_por_servicio_tipo():  
    """
    Obtiene las guardias pendientes de un servicio de acuerdo al tipo, dada una fecha. Tambien recibe el legajo del empleado.
    """
    data = request.get_json()
    servicio_id = data.get('servicio_id')
    tipo = data.get('tipo')
    fecha_inicio_guardia = data.get('fecha_guardia')
    legajo = data.get('legajo_empleado')
    ESTADO_GUARDIA_PENDIENTE = "Pendiente"

    # INICIO Validaciones de datos
    # Validación del servicio 
    validacion_servicio, mensaje = verificar_servicio(servicio_id)
    if not validacion_servicio:
        return jsonify({'error': mensaje}), 404
    
    # Validación del tipo de guardia
    validacion_tipo_guardia, mensaje = validar_tipo_guardia(tipo)
    if not validacion_tipo_guardia:
        return jsonify({'error': mensaje}), 400
    
    # Validación de la fecha_guardia de guardia ingresada
    validacion_fecha, mensaje = validar_fecha_modificar_empleado_guardia(fecha_inicio_guardia)
    if not validacion_fecha:
        return jsonify({'error': mensaje}), 400
    
    # Verificamos que el empleado al que queremos asignar la guardia exista 
    validacion_empleado, mensaje = verificar_EmpleadoID(legajo)
    if not validacion_empleado:
        return jsonify({'error': mensaje}), 400
    
    # Se obtiene el periodo de fechas a la cual pertenece la guardia
    periodo_fecha_guardia, mensaje = obtener_periodo_fecha(fecha_inicio_guardia)
    if not periodo_fecha_guardia:
        return jsonify({'error': mensaje}), 400
    
    periodo_fecha_inicio = periodo_fecha_guardia[0]
    periodo_fecha_fin = periodo_fecha_guardia[1]

    # Se verifica que nuevo empleado no exceda la cantidad de guardias mensuales
    validacion_cantidad_guardias_empleado, mensaje = verificar_cantidad_guardias(legajo, tipo, periodo_fecha_inicio, periodo_fecha_fin, 0.5)
    if not validacion_cantidad_guardias_empleado:
        return jsonify({'error': mensaje}), 400
    # FIN Validaciones de datos

    # Obtenemos las guardias pendientes de un servicio de acuerdo al tipo, dada una fecha
    guardias = Guardia.query.join(ActividadExtraordinaria).filter(
        ActividadExtraordinaria.servicio_id == servicio_id,
        Guardia.tipo == tipo,
        ActividadExtraordinaria.fecha_ini == fecha_inicio_guardia,
        ActividadExtraordinaria.estado == ESTADO_GUARDIA_PENDIENTE,
        ActividadExtraordinaria.legajo_empleado != legajo
    ).all()

    # Esta información será retornada al front, para visualizar y poder seleccionar la guardia
    return jsonify([{
        'id': guardia.id,
        "fecha_inicio": guardia.actividad_extraordinaria.fecha_ini,
        "fecha_fin": guardia.actividad_extraordinaria.fecha_fin,
        "nombre": guardia.actividad_extraordinaria.empleado.nombre,
        "apellido": guardia.actividad_extraordinaria.empleado.apellido,
        'duracion': guardia.duracion,
        'tipo': guardia.tipo,
    } for guardia in guardias])


def modificar_empleado_guardia(id_guardia):
    data = request.get_json()
    legajo_nuevo_empleado = data.get('legajo_empleado')

    validacion_empleado, mensaje = verificar_EmpleadoID(legajo_nuevo_empleado)
    if not validacion_empleado:
        return jsonify({'error': mensaje}), 400

    validacion_guardia, mensaje = verificar_guardia(id_guardia)
    if not validacion_guardia:
        return jsonify({'error': mensaje}), 404
    
    guardia_seleccionada = Guardia.query.get(id_guardia)
    fecha_guardia_seleccionada = str(guardia_seleccionada.actividad_extraordinaria.fecha_ini)

    periodo_fecha_guardia, mensaje = obtener_periodo_fecha(fecha_guardia_seleccionada)
    if not periodo_fecha_guardia:
        return jsonify({'error': mensaje}), 400
    
    periodo_fecha_inicio = periodo_fecha_guardia[0]
    periodo_fecha_fin = periodo_fecha_guardia[1]
    cantidad = int(guardia_seleccionada.duracion) / 24

    # Contabilizamos la cantidad de guardias que tiene el nuevo empleado a asignar
    validacion_cantidad_guardias_empleado, mensaje = verificar_cantidad_guardias(legajo_nuevo_empleado, guardia_seleccionada.tipo, periodo_fecha_inicio, periodo_fecha_fin, cantidad)
    if not validacion_cantidad_guardias_empleado:
        return jsonify({'error': mensaje}), 400

    # Se verifica que ambos empleados tengan el mismo rol
    legajo_empleado_actual = guardia_seleccionada.actividad_extraordinaria.legajo_empleado
    rol_valido, mensaje = verificar_rol_empleados(legajo_empleado_actual, legajo_nuevo_empleado)
    if not rol_valido:
        return jsonify({"error": mensaje}), 400
    
    # Se verifica que no exista alguna superposición con licencias y/o actividades del nuevo empleado
    fecha_inicio_guardia = str(guardia_seleccionada.actividad_extraordinaria.fecha_ini)
    fecha_fin_guardia = str(guardia_seleccionada.actividad_extraordinaria.fecha_fin)
    verificacion_fechas, error = verificar_fechas(fecha_inicio_guardia, fecha_fin_guardia, legajo_nuevo_empleado)
    if not verificacion_fechas:
        return jsonify({'error': error}), 400

    guardia_seleccionada.actividad_extraordinaria.legajo_empleado = legajo_nuevo_empleado
    db.session.commit()

    return jsonify([{
        'mensaje': f"La modificación de la guardia #{id_guardia} fue realizada correctamente. El empleado con legajo {legajo_empleado_actual} fue reemplezado en la guardia #{id_guardia}, por el empleado con legajo {legajo_nuevo_empleado}"
    }]), 200