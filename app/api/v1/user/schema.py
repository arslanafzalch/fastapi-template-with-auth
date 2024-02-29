from datetime import datetime, time
from typing import List

from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    field_validator,
)

from app.models.schema import ModelSchema
from app.schemas.Enums import (
    GenderEnum,
)


class UserRegisterOrLoginRequest(BaseModel):
    """
    Schema for user registration or login request
    """

    email: EmailStr = Field(
        description="Email of the user", example="peterklaven@gmail.com"
    )


class ReadUserForTokenResponse(BaseModel):
    """
    Schema for user. Use to read user from database to check if a token should be generated or not
    """

    id: str
    username: str
    email: EmailStr
    hashed_otp: str | None = None
    otp_created_at: datetime | None = None
    last_login_at: datetime | None = None

    age: int | None = None

    model_config = ConfigDict(from_attributes=True)


class UpdateUserAfterTokenRequest(BaseModel):
    """
    Schema for user update request after token generation
    """

    id: str
    otp: str | None = None
    otp_created_at: datetime | None = None
    last_login_at: datetime | None = datetime.now()


class UserAuthResponse(BaseModel):
    id: str
    otp_created_at: datetime | None = None
    last_login_at: datetime | None = None
    is_active: bool | None = None

    model_config = ConfigDict(from_attributes=True)


class UserProfileRequest(BaseModel):
    """
    Schema for user profile
    """

    full_name: str = Field(
        description="Full name of the user",
        example="Peter Klaven",
    )
    phone_number: str = Field(
        description="Phone number of the user",
        example="1234567890",
    )

    age: int = Field(description="Age of the user", example=25)
    gender: GenderEnum = Field(description="Gender of the user", example="Male")
    height: float = Field(description="Height of the user in cm", example=170.3)
    weight: float = Field(description="Weight of the user kg", example=70.5)

    @field_validator("gender", mode="after")
    @classmethod
    def get_enum_value(cls, v):
        """
        Convert enum values to string
        """
        return v.value if isinstance(v, GenderEnum) else v


class UserProfileUpdateRequest(BaseModel):
    # base user info
    full_name: str | None = Field(
        None,
        description="Full name of the user",
        example="Peter Klaven",
    )
    phone_number: str | None = Field(
        None,
        description="Phone number of the user",
        example="1234567890",
    )

    # user profile info
    age: int | None = Field(None, description="Age of the user", example=25)
    gender: GenderEnum | None = Field(
        None, description="Gender of the user", example="Male"
    )
    height: float | None = Field(
        None, description="Height of the user in cm", example=170.3
    )
    weight: float | None = Field(
        None, description="Weight of the user kg", example=70.5
    )

    @field_validator("gender", mode="after")
    @classmethod
    def get_enum_value(cls, v):
        """
        Convert enum values to string
        """
        return v.value if isinstance(v, GenderEnum) else v


class UserProfileAddOrUpdateResponse(BaseModel):
    details: str | None = Field(
        description="Profile update details", example="Profile updated successfully"
    )


class UserProfileResponse(UserProfileUpdateRequest, ModelSchema):
    email: EmailStr
    username: str | None = None
