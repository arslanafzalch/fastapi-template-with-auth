from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr,
)


class ModelSchema(BaseModel):
    """
    Base schema for all the models. Used for inheriting the model config mostly
    """

    model_config = ConfigDict(from_attributes=True)


class UserSchema(ModelSchema):
    """
    Schema for user model. Used for getting user details
    """

    id: str
    email: EmailStr = Field(
        description="Email of the user", example="darthvader@swars.com"
    )
    username: str | None = Field(
        None, description="Username of the user", example="darthvader"
    )
    hashed_otp: str | None = Field(None, description="Hashed OTP of the user")
    role_id: int | None = Field(None, description="Role ID of the user", example=1)
    updated_at: datetime | None = None
    created_at: datetime | None = None
    otp_created_at: datetime | None = None
    last_login_at: datetime | None = None
