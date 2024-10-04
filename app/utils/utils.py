from datetime import datetime
from app.models import ActividadExtraordinaria, Licencia

def verificar_fechas(fecha_inicio, fecha_fin, empleado_id):
    # Validar si hay superposición de fechas con actividades extraordinarias
    actividades = ActividadExtraordinaria.query.filter(
        ActividadExtraordinaria.empleado_id == empleado_id,
        ActividadExtraordinaria.fecha_inicio <= fecha_fin,
        ActividadExtraordinaria.fecha_fin >= fecha_inicio
    ).all()

    if actividades:
        return False, "Superposición con otra actividad"

    # lógica para validar la licencia
    licencias = Licencia.query.filter(
        Licencia.empleado_id == empleado_id,
        Licencia.fecha_inicio <= fecha_fin,
        Licencia.fecha_fin >= fecha_inicio
    ).all()

    if licencias:
        return False, "Superposición con licencia"

    return True, "Validación exitosa"
