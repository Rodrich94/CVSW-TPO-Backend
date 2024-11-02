# app/routes/__init__.py

from .routerEmpleado import router_empleado  # Importar los blueprints aquí
from .routerTraslado import router_traslado  # Otro ejemplo de blueprint
from .routerDiagramaMensual import router_diagrama
from .routerGuardia import router_guardia
from .routerServicio import router_servicio
from .routerEstablecimiento import router_establecimiento

def register_blueprints(app):
    """
    Esta función registra todos los blueprints de las rutas de la aplicación.
    """
    app.register_blueprint(router_empleado)
    app.register_blueprint(router_traslado)
    app.register_blueprint(router_diagrama)
    app.register_blueprint(router_guardia)
    app.register_blueprint(router_servicio)
    app.register_blueprint(router_establecimiento)

