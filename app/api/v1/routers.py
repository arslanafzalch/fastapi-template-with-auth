from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.api.v1.auth import auth_router
from app.api.v1.role import role_router
from app.api.v1.user import user_router
from app.api.v1.utils import utils_router

from app.schemas.responses import CustomJSONResponse


def include_routers(router_instance) -> None:
    """
    Include all routers to the router instance

    :param router_instance: Router instance

    :return: None
    """
    router_instance.include_router(auth_router, prefix="/auth", tags=["Auth"])
    router_instance.include_router(user_router, prefix="/users", tags=["User"])
    router_instance.include_router(
        role_router, prefix="/roles", tags=["Role"], include_in_schema=False
    )
    router_instance.include_router(utils_router, prefix="/utils", tags=["Utils"])


router = APIRouter(prefix="/api/v1")
include_routers(router)


@router.get(
    "/",
    summary="Home API route",
    status_code=status.HTTP_200_OK,
    response_model=CustomJSONResponse,
    tags=["API"],
)
def home_api():
    """
    # Home API

    This API endpoint is the home API.

    **Valid Roles**
    - `All Users`

    ## Returns
    - A `JSON` response with detail about the API
    """

    return JSONResponse(
        content={
            "message": "Welcome to the API",
            "detail": "This API is built using FastAPI",
            "version": "1.0.0",
        },
    )
