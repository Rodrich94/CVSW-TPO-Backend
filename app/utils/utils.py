from app.models import ActividadExtraordinaria, Licencia

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
