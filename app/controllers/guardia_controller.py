from datetime import datetime
from flask import request, jsonify
from ..models import Guardia, ActividadExtraordinaria, Establecimiento, Servicio, Empleado
from .. import db
from ..utils.utils import verificar_empleado, verificar_fechas, verificar_cupo_mensual, verificar_servicio, validar_tipo_guardia, validar_fechas_guardia, validar_duracion_guardia, verificar_cantidad_guardias

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

def modificar_guardia():
    # Se obtiene el json de la request entrante
    inputs = request.get_json()
    
    # Se guardan los datos por los cuales se va a realizar la búsqueda
    nombre_establecimiento = inputs.get('establecimiento') # Se asume que es un establecimiento válido, ya que es un formulario de selección
    nombre_servicio = inputs.get('servicio') # Se asume que es un servicio válido sobre el establecimiento, ya que es un formulario de selección
    tipo_guardia = inputs.get('tipoGuardia')  # Se asume que es un tipo de guardia válido, ya que es un formulario de selección
    fecha_guardia = inputs.get('fechaGuardia') # Se asume que la fecha es de día actual en adelante
    legajo_empleado = inputs.get('legajoEmpleado')
    guardia_id = inputs.get('idGuardia') # Se asume que es una guardia existente, dado que se accede mediante selección/botón
    ESTADO_ACTIVIDAD = "Pendiente"

    servicio_establecimiento_filtrado = db.session.query((Servicio)).join(Establecimiento). \
                                                          filter(Establecimiento.nombre == nombre_establecimiento,
                                                                 Servicio.nombre == nombre_servicio).first()

    print(f"[Establecimiento: {servicio_establecimiento_filtrado.establecimiento.nombre}, Servicio: {servicio_establecimiento_filtrado.nombre}]")

    empleado_filtrado = db.session.query(Empleado).filter_by(legajo = legajo_empleado).first()
    if empleado_filtrado:
        guardias_pendientes = db.session.query(ActividadExtraordinaria.fecha_ini, ActividadExtraordinaria.fecha_fin, 
                                               Empleado.nombre, Empleado.apellido, Empleado.legajo, Empleado.rol). \
                                                select_from(Guardia).join(ActividadExtraordinaria).join(Empleado). \
                                                filter(Guardia.tipo == tipo_guardia, 
                                                       ActividadExtraordinaria.servicio_id == servicio_establecimiento_filtrado.id,
                                                       ActividadExtraordinaria.fecha_ini == fecha_guardia,
                                                       ActividadExtraordinaria.estado == ESTADO_ACTIVIDAD,
                                                       ActividadExtraordinaria.legajo_empleado != empleado_filtrado.legajo)#. \
                                                #all()

        if guardias_pendientes: 
            for guardia in guardias_pendientes:
                print(f"""[Fecha inicio: {guardia.fecha_ini}, Fecha fin: {guardia.fecha_fin}, Nombre: {guardia.nombre}, Apellido: {guardia.apellido}]""") 

            guardia_pendiente_seleccionada = guardias_pendientes.filter(ActividadExtraordinaria.id == guardia_id).first()
            print(f"""Guardia seleccionada: [Fecha inicio: {guardia_pendiente_seleccionada.fecha_ini}, Fecha fin: {guardia_pendiente_seleccionada.fecha_fin}, Nombre: {guardia_pendiente_seleccionada.nombre}, Apellido: {guardia_pendiente_seleccionada.apellido}]""")

            if guardia_pendiente_seleccionada.rol == empleado_filtrado.rol:
                validacion, mensaje = verificar_fechas(guardia_pendiente_seleccionada.fecha_ini, 
                                 guardia_pendiente_seleccionada.fecha_fin, 
                                 empleado_filtrado.legajo)
                if validacion:
                    #print(guardia_pendiente_seleccionada.legajo)
                    guardia_pendiente_seleccionada.legajo = empleado_filtrado.legajo
                    #db.session.commit()
                    #print(mensaje)
                    return jsonify({"message": "Cambio de empleado en guardia se realizó correctamente", 
                                    "guardia": str(guardia_pendiente_seleccionada)}), 200
                else:
                    return jsonify({"error": mensaje}), 400
            else:
                mensaje = "Rol no coincidente entre empleados."
                #print("Rol no coincidente entre empleados.")
        else:
            mensaje = f"No existen guardias {tipo_guardia}s."
            #print(f"No existen guardias {tipo_guardia}s.")
    else:
        mensaje = "Empleado inexistente."
        #print("Empleado inexistente.")
    return jsonify({"error": mensaje}), 400


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
