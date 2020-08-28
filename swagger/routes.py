from flask import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint

from task_manager import settings

SWAGGER_SCHEMA_ROUTE = "/swagger.json"
API_URL = f"{settings.BASE_URL}{settings.SWAGGER_URL}{SWAGGER_SCHEMA_ROUTE}"
swagger = get_swaggerui_blueprint(settings.SWAGGER_URL, API_URL)


@swagger.route(SWAGGER_SCHEMA_ROUTE)
def swagger_schema():
    return send_from_directory("../swagger", "swagger.json")
