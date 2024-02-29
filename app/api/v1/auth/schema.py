from pydantic import EmailStr, Field, BaseModel


class CreateUserTokenRequest(BaseModel):
    """
    Schema for user token request, used for login and getting the tokens
    """

    email: EmailStr = Field(
        description="Email of the user", example="peterklaven@gmail.com"
    )
    otp: str = Field(
        description="OTP sent to user email",
        example="1234",
    )


class CreateUserTokenResponse(BaseModel):
    """
    Schema for user token response, used for login and getting the tokens
    """

    username: str = Field(
        description="Username of the user",
        example="peterklaven",
    )
    access_token: str = Field(
        description="Access token of the user", example="eycakm.m38huy8(Y8hci..."
    )
    refresh_token: str = Field(
        description="Refresh token of the user", example="eycakm.m38huy8(Y8hci..."
    )

    is_new_user: bool = Field(
        description="Use to check if user's profile has been created or not",
        example=True,
    )
