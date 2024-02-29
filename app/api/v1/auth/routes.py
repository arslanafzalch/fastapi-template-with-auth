from datetime import timedelta

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from fastapi_another_jwt_auth.exceptions import MissingTokenError, JWTDecodeError

from app.core.constants import (
    ACCESS_TOKEN_EXPIRES_IN,
    REFRESH_TOKEN_EXPIRES_IN,
    OTP_EXPIRED_TIME,
    DEBUG_MODE,
)
from app.api.v1.auth.schema import (
    CreateUserTokenRequest,
    CreateUserTokenResponse,
)
from app.api.v1.user.operations import ReadUserForToken, ReadUser
from app.api.v1.user.operations import UpdateUserForToken
from app.api.v1.user.schema import UpdateUserAfterTokenRequest
from app.controllers.utils import verify_hashed_text, get_current_timestamp
from app.logger import logger
from app.schemas.responses import (
    common_responses,
    CustomUnAuthorizedResponse,
    CustomJSONResponse,
)
from app.services.oauth2 import AuthJWT, protected_route

router = APIRouter()

log = logger.extendable_logger(log_name="Auth")


@router.post(
    "/token",
    summary="Get tokens for a user",
    status_code=status.HTTP_201_CREATED,
    **common_responses(include_model=False),
    response_model=CreateUserTokenResponse,
)
async def get_token(
    payload: CreateUserTokenRequest,
    read_operation: ReadUserForToken = Depends(ReadUserForToken),
    update_operation: UpdateUserForToken = Depends(UpdateUserForToken),
    authorize: AuthJWT = Depends(),
):
    """
    # Get tokens for a user

    This API endpoint allows user to get tokens by providing OTP.

    **Valid Roles:**
    - `All Users`

    ## Returns:
    - A `JSON` response having tokens (access and refresh) for the user
    """

    user = await read_operation.execute(email=payload.email)  # Check if the user exist

    if DEBUG_MODE:
        if (
            user.last_login_at is not None  # User is already logged in
            and (user.last_login_at + timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
            >= get_current_timestamp()  # Access token is not expired
        ):
            return JSONResponse(
                status_code=status.HTTP_208_ALREADY_REPORTED,
                content={"detail": "You are logged in."},
            )

    # Check if OTP is generated
    if user.hashed_otp is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has not requested OTP yet",
        )

    # Check if the OTP is valid
    if not verify_hashed_text(payload.otp, user.hashed_otp):
        # Check if OTP is expired
        if (
            user.otp_created_at + timedelta(seconds=OTP_EXPIRED_TIME)
        ) < get_current_timestamp():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OTP expired",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect OTP",
        )

    try:
        update_payload = UpdateUserAfterTokenRequest(
            id=user.id,
            otp=None,
            otp_created_at=None,
            last_login_at=get_current_timestamp(),
        )
        await update_operation.execute(update_payload)

    except Exception as e:
        log.error(e, exc_info=1)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not login. Try again",
        )

    try:
        # Create access token
        access_token = authorize.create_access_token(
            subject=str(user.id),
            expires_time=timedelta(
                minutes=ACCESS_TOKEN_EXPIRES_IN
            ),  # setting the expiry time for the access token from the config files
        )

        # Create refresh token
        refresh_token = authorize.create_refresh_token(
            subject=str(user.id),
            expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN),
        )

        # Send both access and refresh token
        return CreateUserTokenResponse(
            is_new_user=user.age
            is None,  # True if age is None else False, use to redirect to profile page or to dashboard
            access_token=access_token,
            refresh_token=refresh_token,
            username=user.username,
        )

    except Exception as e:
        log.error(e, exc_info=1)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get(
    "/refresh",
    summary="Get new access token",
    status_code=status.HTTP_201_CREATED,
    **common_responses(),
    operation_id="authorize_refresh_access_token",
)
async def refresh_access_token(
    authorize: AuthJWT = Depends(), read_operation: ReadUser = Depends(ReadUser)
):
    """
    # Get new access token

    This API endpoint allows user to get new access token using refresh token.

    **Valid Roles:**
    - `All Authorized Users`

    ## Returns:
    - A `JSON` response having new access token
    """

    try:
        authorize.jwt_refresh_token_required()  # Check if refresh token is valid

        _id = authorize.get_jwt_subject()  # Get username from refresh token

        if not _id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh access token",
            )

        user = await read_operation.execute(_id)  # Check if the user exist
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user belonging to this token no logger exist",
            )

        access_token = authorize.create_access_token(  # Create new access token
            subject=str(user.id),
            expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
        )

        return JSONResponse(
            content={
                "access_token": access_token,
            },
        )

    except Exception as e:
        if hasattr(e, "message") and e.message == "Signature has expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired, login again",
            )
        if isinstance(e, MissingTokenError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide refresh token",
            )
        if isinstance(e, JWTDecodeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e) or "Internal Server Error",
        )


@router.get(
    "/logout",
    summary="Logout user",
    status_code=status.HTTP_200_OK,
    response_model=CustomJSONResponse,
    responses={
        401: {
            "model": CustomUnAuthorizedResponse,
            "description": "Unauthorized",
        }
    },
    operation_id="authorize_logout_user",
)
async def logout_user(
    update_operation: UpdateUserForToken = Depends(UpdateUserForToken),
    user_id: str = Depends(protected_route),
):
    """
    # Logout user

    This API endpoint allows user to logout.

    **Valid Roles:**
    - `All Authorized Users`

    ## Returns:
    - A `JSON` response having message about logout
    """
    update_data = UpdateUserAfterTokenRequest(
        id=user_id, last_login_at=None, otp=None, otp_created_at=None
    )
    await update_operation.execute(payload=update_data)

    return JSONResponse(
        content={
            "message": "Successfully logged out",
        },
    )
