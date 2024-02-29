from fastapi import APIRouter, status

from app.core.constants import PROJECT_NAME
from app.schemas.responses import (
    CustomJSONResponse,
)


def include_routers(router_instance) -> None:
    """
    Include all routers to the router instance

    :param router_instance: Router instance

    :return: None
    """
    pass


router = APIRouter()
include_routers(router)


@router.get(
    "/",
    summary="Admin API Home",
    status_code=status.HTTP_200_OK,
    response_model=CustomJSONResponse,
    operation_id="admin_home",
    tags=["Home"],
)
async def admin_api_home():
    """
    # Admin API Home

    This API endpoint is the home of the admin_api.

    **Valid Roles**
    - `All Users`

    ## Returns
    - A `JSON` response with detail about the admin_api
    """

    return {"detail": f"{PROJECT_NAME} Backend"}
