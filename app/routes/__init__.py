# app/routes/__init__.py

from .routesEmpleado import router_empleado  # Importar los blueprints aquí
from .routerTraslado import router_traslado  # Otro ejemplo de blueprint
from .routerDiagramaMensual import router_diagrama
def register_blueprints(app):
    """
    Esta función registra todos los blueprints de las rutas de la aplicación.
    """
    app.register_blueprint(router_empleado)
    app.register_blueprint(router_traslado)
    app.register_blueprint(router_diagrama)
