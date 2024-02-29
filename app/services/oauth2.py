from typing import List

from fastapi import Depends, HTTPException, status
from fastapi_another_jwt_auth import AuthJWT
from fastapi_another_jwt_auth.exceptions import InvalidHeaderError
from pydantic import BaseModel

from app.api.v1.user.operations import ReadUser
from app.config import settings
from app.controllers.exceptions import NotFoundException
from app.logger import logger

log = logger.extendable_logger(log_name="OAuth2")


class Settings(BaseModel):
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [settings.JWT_ALGORITHM]
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_access_cookie_key: str = "access_token"
    authjwt_refresh_cookie_key: str = "refresh_token"
    authjwt_cookie_csrf_protect: bool = False
    authjwt_secret_key: str = settings.JWT_SECRET_KEY


@AuthJWT.load_config
def get_config() -> Settings:
    return Settings()


async def protected_route(
    read_operation: ReadUser = Depends(ReadUser), authorize: AuthJWT = Depends()
) -> str:
    try:
        authorize.jwt_required()
        _id = authorize.get_jwt_subject()

        user = await read_operation.execute_for_auth(_id=_id)
        if not user.is_active:  # User is not active or has been deleted
            raise NotFoundException("User no longer exist")

        if (
            user.last_login_at is None
        ):  # User is logging in for the first time or has logged out
            raise NotFoundException(
                detail="Log in first to access this route",
            )

    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail)

    except Exception as e:
        error = e.__class__.__name__

        if error == "InvalidHeaderError":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token. Should be a 'Bearer <token>'",
            )

        if error == "MissingTokenError":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not logged in. Token is Missing",
            )

        if hasattr(e, "message") and e.message == "Signature has expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired, login again",
            )

        log.error(e, exc_info=1)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
        )

    return user.id
