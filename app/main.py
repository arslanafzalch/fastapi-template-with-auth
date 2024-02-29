from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import status

from app.api import api_router
from app.core.constants import (
    ADMIN_SITE_REQUIRED,
    PROJECT_NAME,
    PROJECT_VERSION,
    PROJECT_DESCRIPTION,
)
from app.core.register import register_app
from app.schemas.responses import (
    CustomJSONResponse,
    CustomInternalServerResponse,
)
from app.services.database import sessionmanager


# if sys.platform == "win32":
#     loop = asyncio.ProactorEventLoop()
#     asyncio.set_event_loop(loop)


@asynccontextmanager
async def engine_lifespan(lifespan_app: FastAPI):
    """
    Function that handles startup and shutdown events.
    """
    yield
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()


def start_application(lifespan_fn) -> FastAPI:
    """
    Function to start the application

    :param lifespan_fn: Function to handle startup and shutdown events

    :return: FastAPI instance
    """
    app_instance = FastAPI(
        lifespan=lifespan_fn,
        title=PROJECT_NAME,
        version=PROJECT_VERSION,
        description=PROJECT_DESCRIPTION,
        docs_url="/api/v1/docs",
        openapi_url="/api/v1/openapi.json",
        redoc_url="/api/v1/redoc",
        debug=False,
    )

    app_instance.include_router(api_router)

    register_app(app_instance, admin_site=ADMIN_SITE_REQUIRED)

    return app_instance


app = start_application(engine_lifespan)


@app.get(
    "/",
    summary="API Home",
    status_code=status.HTTP_200_OK,
    response_model=CustomJSONResponse,
    operation_id="home",
    tags=["Home"],
)
def home():
    """
    # Home

    This API endpoint is the home.

    **Valid Roles**
    - `All Users`

    ## Returns
    - A `JSON` response with detail about the backend
    """

    return {"detail": f"{PROJECT_NAME} Backend"}
