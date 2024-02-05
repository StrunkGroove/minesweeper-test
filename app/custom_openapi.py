from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


app = FastAPI()


def create_openapi_schema():
    return get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        terms_of_service=app.terms_of_service,
        contact=app.contact,
        license_info=app.license_info,
        routes=app.routes,
        tags=app.openapi_tags,
        servers=app.servers,
    )

def remove_validation_errors_schemas(openapi_schema):
    for schema in list(openapi_schema["components"]["schemas"]):
        if schema == "HTTPValidationError" or schema == "ValidationError":
            del openapi_schema["components"]["schemas"][schema]

def order_schemas(openapi_schema):
    schema_order = [
        "GameNewRequest",
        "GameTurnRequest",
        "MineFieldRow",
        "GameInfoResponse",
        "ErrorResponse",
    ]
    components_schemas = openapi_schema.get("components", {}).get("schemas", {})
    ordered_schemas = {schema_name: components_schemas[schema_name] for schema_name in schema_order if schema_name in components_schemas}
    openapi_schema["components"]["schemas"] = ordered_schemas

def remove_422_response(openapi_schema):
    for _, method_item in openapi_schema.get('paths').items():
        for _, param in method_item.items():
            responses = param.get('responses')
            if '422' in responses:
                del responses['422']

def custom_openapi():
    if not app.openapi_schema:
        openapi_schema = create_openapi_schema()
        remove_validation_errors_schemas(openapi_schema)
        order_schemas(openapi_schema)
        remove_422_response(openapi_schema)
        app.openapi_schema = openapi_schema
        return app.openapi_schema
