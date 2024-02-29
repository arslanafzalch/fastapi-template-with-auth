import secrets
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, APIRouter, BackgroundTasks, Path
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.api.v1.user.operations import (
    CreateUser,
    UpdateUserForToken,
    CreateUpdateUserProfile,
    ReadUserProfile,
)
from app.api.v1.user.schema import (
    UserRegisterOrLoginRequest,
    UpdateUserAfterTokenRequest,
    UserProfileRequest,
    UserProfileUpdateRequest,
    UserProfileResponse,
    UserProfileAddOrUpdateResponse,
)
from app.config import settings
from app.controllers.exceptions import (
    CouldNotPerformDBOperationException,
    CouldNotSentEmailException,
)
from app.controllers.utils import hash_text, get_current_timestamp
from app.core.constants import PROJECT_NAME
from app.logger import logger
from app.schemas.responses import (
    common_responses,
    CustomJSONResponse,
    CustomAlreadyReportedResponse,
    CustomServiceUnavailableResponse,
)
from app.services.mail import sent_otp_in_email
from app.services.oauth2 import protected_route

router = APIRouter()
log = logger.extendable_logger(log_name="User")

OTP_EXPIRED_TIME = settings.OTP_EXPIRED_TIME
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
DEBUG_MODE = settings.DEBUG_MODE


@router.post(
    "",
    summary="Register or login a User",
    status_code=status.HTTP_201_CREATED,
    response_model=CustomJSONResponse,
    responses={
        208: {
            "model": CustomAlreadyReportedResponse,
        },
        503: {
            "model": CustomServiceUnavailableResponse,
        },
    },
)
async def register_or_login_user(
    payload: UserRegisterOrLoginRequest,
    background_tasks: BackgroundTasks,
    create_operation: CreateUser = Depends(CreateUser),
    update_operation: UpdateUserForToken = Depends(UpdateUserForToken),
):
    """
    # Get OTP for new or existing user

    This API endpoint generates OTP for new or existing user.

    **Valid Roles:**
    - `All Users`

    ## Returns:
    - A `JSON` response with details about the response
    """

    user = await create_operation.execute(payload)

    if DEBUG_MODE:
        #  TODO: Add a check for user's last login time hence condition should be `not DEBUG_MODE`
        if (
            user.last_login_at is not None  # User is already logged in
            and (user.last_login_at + timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
            >= get_current_timestamp()  # Access token is not expired
        ):
            return JSONResponse(
                status_code=status.HTTP_208_ALREADY_REPORTED,
                content={"detail": "You are logged in."},
            )

        if user.otp_created_at is not None:  # OTP is already generated
            time_diff = user.otp_created_at + timedelta(seconds=OTP_EXPIRED_TIME)
            secs_to_retry = time_diff - get_current_timestamp()

            if (
                not time_diff < get_current_timestamp()
            ):  # Current OTP is not expired yet
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Try again in {secs_to_retry.seconds} seconds",
                )

    try:
        otp = "".join(str(secrets.randbelow(9) + 1) for i in range(4))  # generating otp

        if not DEBUG_MODE:
            await sent_otp_in_email(  # sending otp to user email
                background_tasks=background_tasks,
                email=user.email,
                data={"name": user.email, "otp": otp, "project_name": PROJECT_NAME},
            )

        update_data = UpdateUserAfterTokenRequest(
            id=user.id,
            otp=hash_text(otp),
            otp_created_at=datetime.now(),
            last_login_at=None,
        )
        await update_operation.execute(update_data)

    except CouldNotSentEmailException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.detail,
        )

    except Exception as e:
        log.error(e, exc_info=1)

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not sent email",
        )

    response = {"detail": "OTP sent to email"}

    if DEBUG_MODE:
        response["otp"] = otp

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=jsonable_encoder(response),
    )


@router.post(
    "/{username}",
    summary="Add profile of a User",
    status_code=status.HTTP_201_CREATED,
    **common_responses(include_model=False),
    response_model=UserProfileAddOrUpdateResponse,
    operation_id="authorize_add_user_profile",
)
async def add_user_profile(
    payload: UserProfileRequest,
    username: str = Path(
        ..., description="The username of the user to retrieve", example="john"
    ),
    user_id: str = Depends(protected_route),
    create_profile_operation: CreateUpdateUserProfile = Depends(
        CreateUpdateUserProfile
    ),
) -> UserProfileAddOrUpdateResponse:
    """
    # Add profile of a User

    This API endpoint adds profile of a user.

    **Valid Roles:**
    - `All Users`

    ## Path Parameters:
    - `username`: The username of the user to retrieve.

    ## Returns:
    - A `JSON` response with details about the response
    """

    await create_profile_operation.execute(user_id=user_id, payload=payload)

    return UserProfileAddOrUpdateResponse(details="Profile added")


@router.patch(
    "/{username}",
    summary="Update profile of a User",
    status_code=status.HTTP_200_OK,
    **common_responses(include_model=False),
    response_model=UserProfileAddOrUpdateResponse,
    operation_id="authorize_update_user_profile",
)
async def update_user_profile(
    payload: UserProfileUpdateRequest,
    username: str = Path(
        ..., description="The username of the user to retrieve", example="john"
    ),
    user_id: str = Depends(protected_route),
    update_profile_operation: CreateUpdateUserProfile = Depends(
        CreateUpdateUserProfile
    ),
) -> UserProfileAddOrUpdateResponse:
    """
    # Update profile of a User

    This API endpoint updates profile of a user.

    **Valid Roles:**
    - `All Users`

    ## Path Parameters:
    - `username`: The username of the user to retrieve.

    ## Returns:
    - A `JSON` response with details about the response
    """

    await update_profile_operation.execute(user_id=user_id, payload=payload)

    return UserProfileAddOrUpdateResponse(details="Profile updated")


@router.get(
    "/{username}",
    summary="Get profile of a User",
    status_code=status.HTTP_200_OK,
    **common_responses(include_model=False),
    response_model=UserProfileResponse,
    operation_id="authorize_get_user_profile",
)
async def get_user_profile(
    username: str = Path(
        ..., description="The username of the user to retrieve", example="john"
    ),
    user_id: str = Depends(protected_route),
    read_user_operation: ReadUserProfile = Depends(ReadUserProfile),
) -> UserProfileResponse:
    """
    # Get profile of a User

    This API endpoint gets profile of a user.

    **Valid Roles:**
    - `All Authorized Users`

    ## Path Parameters:
    - `username`: The username of the user to retrieve.

    ## Returns:
    - A `JSON` response with details about the response
    """

    user = await read_user_operation.execute(_id=user_id)

    return UserProfileResponse.model_validate(user)
