from flask import request, jsonify
from ..utils.utils import verificar_empleado, validar_rango_fechas, obtener_actividades_empleado, verificar_servicio, obtener_resumen_actividades_empleado


def obtener_actividades(legajo_empleado):
    """
    Consulta de actividades por empleado.
    """
    data = request.args
    fecha_desde = data.get('fecha_desde')
    fecha_hasta = data.get('fecha_hasta')

    # Verificar empleado
    empleado_valido, error = verificar_empleado(legajo_empleado)
    if not empleado_valido:
        return jsonify({'error': error}), 400

    # Validar fechas desde y hasta
    fechas_validas, error = validar_rango_fechas(fecha_desde, fecha_hasta)
    if not fechas_validas:
        return jsonify({'error': error}), 400

    # Obtener actividades
    actividades = obtener_actividades_empleado(legajo_empleado, fecha_desde, fecha_hasta)

    return jsonify(actividades), 200


def obtener_resumen_actividades_por_servicio(id_servicio):
    """
    Resumen de actividades por servicio.
    """
    data = request.args
    fecha_desde = data.get('fecha_desde')
    fecha_hasta = data.get('fecha_hasta')

    # Verificar servicio
    validacion_servicio, mensaje = verificar_servicio(id_servicio)
    if not validacion_servicio:
        return jsonify({'error': mensaje}), 404
    
    validacion_fechas, mensaje = validar_rango_fechas(fecha_desde, fecha_hasta)
    if not validacion_fechas:
        return jsonify({'error': mensaje}), 400

    # Obtener el resumen de las actividades de un servicio de cada empleado
    resumen_actividades_por_servicio = obtener_resumen_actividades_empleado(id_servicio, fecha_desde, fecha_hasta)

    return jsonify(resumen_actividades_por_servicio), 200