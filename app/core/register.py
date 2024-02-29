import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from app.controllers.exception_handlers import register_exception_handler
from app.api.admin import admin_api_router
from app.core.constants import PROJECT_NAME, PROJECT_VERSION, PROJECT_DESCRIPTION


def register_app(app: FastAPI, admin_site=True):
    register_exception_handler(app)
    register_mount(app)
    register_middleware(app)
    register_schema(app)

    if admin_site:
        register_admin_app(app)


def register_admin_app(app: FastAPI):
    admin_api = FastAPI()
    admin_api.include_router(admin_api_router)

    app.mount("/admin", admin_api, name="admin_api")


def register_mount(app: FastAPI):
    if not os.path.exists("./app/static"):
        os.mkdir("./app/static")

    app.mount(
        "/static",
        StaticFiles(directory="app/static"),
        name="static",
    )


def register_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_schema(app: FastAPI):
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=PROJECT_NAME,
            version=PROJECT_VERSION,
            description=PROJECT_DESCRIPTION,
            routes=app.routes,
        )

        openapi_schema["components"]["securitySchemes"] = {
            "Bearer Auth": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
                "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token",
            }
        }

        # Get routers from index 4 because before that fastapi define router for /openapi.json, /redoc, /docs, etc.,
        # Get all router where operation_id is authorized
        router_authorize = [
            route
            for route in app.routes[4:]
            if hasattr(route, "operation_id")
            and route.operation_id
            and route.operation_id.split("_")[0]
            == "authorize"  # Get all router where operation_id is authorized
        ]
        for route in router_authorize:
            method = list(route.methods)[0].lower()
            path = getattr(route, "path")
            openapi_schema["paths"][path][method]["security"] = [{"Bearer Auth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
