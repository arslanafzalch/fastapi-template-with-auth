from typing import AsyncIterator

from sqlalchemy.exc import IntegrityError

from app.api.v1.operation import BaseOperation
from app.api.v1.user.schema import (
    UserRegisterOrLoginRequest,
    UpdateUserAfterTokenRequest,
    ReadUserForTokenResponse,
    UserProfileRequest,
    UserProfileUpdateRequest,
    UserProfileResponse,
    UserAuthResponse,
)
from app.controllers.exceptions import (
    NotFoundException,
    CouldNotPerformDBOperationException,
)
from app.models import User, UserSchema


class CreateUser(BaseOperation):
    """
    Used for both register and login apis of the user
    """

    async def execute(self, payload: UserRegisterOrLoginRequest) -> UserSchema:
        """
        Used for both register and login apis of the user

        :param payload: ``(UserRegisterOrLoginRequest)``: The payload for the request.

        :return: ``(UserSchema)``: The user schema object.

        :raises: ``NotFoundException``: If user is not found.
        """
        user = await User.read_by_email(
            self.session, email=payload.email
        )  # get the user by email

        if user is None:  # if user is not found, create new user
            # TODO: get the role_id from the role table and make it dynamic
            user = await User.create(self.session, payload, role_id=1)

        return UserSchema.model_validate(user)


class UpdateUserForToken(BaseOperation):
    """
    Used to update the user for token operations
    """

    async def execute(
        self,
        payload: UpdateUserAfterTokenRequest,
    ) -> None:
        """
        Used to update the user for token operations

        :param payload: ``(UpdateUserAfterTokenRequest)``: The payload for the request.

        :return: None

        :raises: ``NotFoundException``: If user is not found.
        """
        user = await User.read(self.session, _id=payload.id)
        if not user:
            raise NotFoundException("User not found")
        await user.update_for_token(self.session, data=payload)


class CreateUpdateUserProfile(BaseOperation):
    """Used for both create and update profiles apis of the user"""

    async def execute(
        self,
        user_id: str,
        payload: UserProfileRequest | UserProfileUpdateRequest,
    ) -> None:
        """
        Used for both create and update profiles apis of the user

        :param user_id: ``(str)``: The user id.
        :param payload: ``(UserProfileRequest | UserProfileUpdateRequest)``: The payload for the request.

        :return: None

        :raises: ``NotFoundException``: If user is not found.
        :raises: ``CouldNotPerformDBOperationException``: If user update failed.
        """

        user = await User.read(self.session, _id=user_id)  # get the user by id
        if not user:
            raise NotFoundException("User not found")

        # `if` conditions to check whether the payload has the attribute or not
        # as we are using same operation for both read and update profile

        # Base User Info
        if payload.full_name:
            user.full_name = payload.full_name
        if payload.phone_number:
            user.phone_number = payload.phone_number

        # User Profile Info
        if payload.age:
            user.age = payload.age
        if payload.weight:
            user.weight = payload.weight
        if payload.height:
            user.height = payload.height
        if payload.gender:
            user.gender = payload.gender

        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise CouldNotPerformDBOperationException(
                extra="(User Update Failed) " + str(e)
            )


class ReadAllUser(BaseOperation):
    """
    Used to read all users
    """

    async def execute(self) -> AsyncIterator[UserSchema]:
        """
        Used to read all users

        :return: ``(AsyncIterator[UserSchema])``: The user schema object.

        :raises: ``NotFoundException``: If user is not found.
        """
        async for user in User.read_all(self.session, include_role=True):
            yield UserSchema.model_validate(user)


class ReadUserForToken(BaseOperation):
    """
    Used to read user for token operations
    """

    async def execute(self, email: str) -> ReadUserForTokenResponse:
        """
        Used to read user for token operations

        :param email: ``(str)``: The email of the user.

        :return: ``(ReadUserForTokenResponse)``: The user for token response object.
        """
        user = await User.read_by_email(self.session, email=email)
        if not user:
            raise NotFoundException("User not found")

        return ReadUserForTokenResponse.model_validate(user)


class ReadUser(BaseOperation):
    """
    Used for both read profile apis of the user and for the response of add profile
    """

    async def execute(self, _id) -> UserSchema | None:
        """
        Used for both read profile apis of the user and for the response of add profile

        :param _id: ``(str)``: The user id.

        :return: ``(UserSchema | None)``: The user schema object.
        """
        user = await User.read(self.session, _id=_id)
        if not user:
            raise NotFoundException("User not found")
        return UserSchema.model_validate(user)

    async def execute_for_auth(self, _id) -> UserAuthResponse:
        """
        Used for both read profile apis of the user and for the response of add profile

        :param _id: ``(str)``: The user id.

        :return: ``(UserAuthResponse)``: The user auth response object.
        """
        user = await User.read_for_auth(self.session, _id=_id)
        if not user:
            raise NotFoundException("User not found")
        return UserAuthResponse.model_validate(user)


class ReadUserProfile(BaseOperation):
    """Used for both read profile apis of the user and for the response of add profile"""

    async def execute(self, _id) -> UserProfileResponse | None:
        """
        Used for both read profile apis of the user and for the response of add profile

        :param _id: ``(str)``: The user id.

        :return: ``(UserProfileResponse | None)``: The user profile response object.
        """
        user = await User.read(self.session, _id=_id)
        if not user:
            raise NotFoundException("User not found")

        return UserProfileResponse.model_validate(user)
