from __future__ import annotations

from typing import Optional, TYPE_CHECKING, AsyncIterator
from uuid import uuid4

from sqlalchemy import (
    String,
    ForeignKeyConstraint,
    select,
    update as sql_update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    selectinload,
    load_only,
)

from app.controllers.exceptions import CouldNotPerformDBOperationException
from app.controllers.utils import generate_random_number
from app.models.base_users import BaseUser
from app.models.roles import Role

if TYPE_CHECKING:
    from app.api.v1.user.schema import (
        UserRegisterOrLoginRequest,
        UpdateUserAfterTokenRequest,
        UserProfileRequest,
        UserProfileUpdateRequest,
    )


class User(BaseUser):
    """
    Table used to store the all users (that are using the service).
    """

    __tablename__ = "users"

    # Primary Key / Foreign Key
    base_user_id: Mapped[str] = mapped_column(
        String(50), primary_key=True
    )  # same as the id from the base_user table

    # Main data fields
    age: Mapped[Optional[int]] = mapped_column(nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    height: Mapped[Optional[float]] = mapped_column(nullable=True)
    weight: Mapped[Optional[float]] = mapped_column(nullable=True)

    # Foreign Keys

    # Relationships

    # Meta data

    __mapper_args__ = {
        "polymorphic_identity": "user",
    }

    __table_args__ = (
        ForeignKeyConstraint(["base_user_id"], ["base_users.id"], ondelete="CASCADE"),
    )

    @classmethod
    async def create(
        cls, session: AsyncSession, data: UserRegisterOrLoginRequest, **kwargs
    ) -> User:
        """
        Function to create a new user to database

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param data: ``(UserRegisterOrLoginRequest)``: The data to create a new user.
        :param kwargs: ``(dict)``: The extra data to create a new user.

        :return: BaseUser: The newly created user.

        :raises: CouldNotPerformDBOperation: If the creation operation fails.
        """
        username = data.email.split("@")[0]
        stmt = select(cls.id).where(cls.username == username)
        user = await session.scalar(stmt)

        if (
            user is not None
        ):  # if user with same username exists, add random number to username
            username = username + str(generate_random_number())

        user = cls(id=str(uuid4()), username=username, **data.model_dump(), **kwargs)
        session.add(user)

        try:
            await session.commit()
            await session.refresh(user)

        except Exception as e:
            await session.rollback()

            err_cls = ""
            if isinstance(e, IntegrityError):
                err_cls = " - Integrity Error"

            err_cause = None
            if hasattr(e, "orig") and hasattr(e.orig, "args"):
                err_cause = str(e.orig.args[1])

            raise CouldNotPerformDBOperationException(
                extra=(
                    f"(User Creation Failed{err_cls})" + (" -> " + err_cause)
                    if err_cause
                    else ""
                )
            )

        return user

    @classmethod
    async def read(
        cls,
        session: AsyncSession,
        _id: str,
        include_role: bool = False,
    ) -> User | None:
        """
        Read a user by its unique identifier.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param _id: ``(str)``: The unique identifier of the user to retrieve.
        :param include_role: ``(bool)``: Flag to indicate if associated role should be eagerly loaded. Defaults to False.

        :return: BaseUser | None: The BaseUser object if found, otherwise None.
        """
        stmt = select(cls).where(cls.id == _id)

        if include_role:
            stmt = stmt.options(
                selectinload(cls.role).load_only(Role.id, Role.name, raiseload=True)
            )

        return await session.scalar(stmt)

    @classmethod
    async def read_for_auth(
        cls,
        session: AsyncSession,
        _id: str,
    ) -> User | None:
        """
        Read a user by its unique identifier.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param _id: ``(str)``: The unique identifier of the user to retrieve.

        :return: BaseUser | None: The BaseUser object if found, otherwise None.
        """
        stmt = (
            select(cls)
            .where(cls.id == _id)
            .options(
                load_only(  # these are the columns that is needed for authentication check
                    cls.id, cls.last_login_at, cls.otp_created_at, cls.is_active
                )
            )
        )

        user = await session.execute(stmt)
        return user.scalars().one_or_none()

    @classmethod
    async def read_by_email(
        cls, session: AsyncSession, email: str, include_role: bool = False
    ) -> User | None:
        """
        Read a user by its unique email.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param email: ``(str)``: The unique email of the user to retrieve.
        :param include_role: ``(bool)``: Flag to indicate if associated role should be eagerly loaded. Defaults to False.

        :return: BaseUser | None: The BaseUser object if found, otherwise None.
        """
        stmt = select(cls).where(cls.email == email)

        if include_role:
            stmt = stmt.options(
                selectinload(cls.role).load_only(Role.id, Role.name, raiseload=True)
            )

        return await session.scalar(stmt)

    @classmethod
    async def read_all(
        cls, session: AsyncSession, include_role: bool = False
    ) -> AsyncIterator[User]:
        """
        Retrieve all user from the database asynchronously.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param include_role: ``(bool)``: Flag to indicate if associated role should be eagerly loaded. Defaults to False.

        :return: AsyncIterator[BaseUser]: An asynchronous iterator yielding BaseUser objects.
        """
        stmt = select(cls)

        if include_role:
            stmt = stmt.options(
                selectinload(cls.role).load_only(Role.id, Role.name, raiseload=True)
            )

        stream = await session.stream_scalars(stmt.order_by(cls.id))

        async for row in stream:
            yield row

    async def update_for_token(
        self, session: AsyncSession, data: UpdateUserAfterTokenRequest
    ) -> None:
        """
        Update a user.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param data: ``(UpdateBaseUserRequest)``: The data to update a user.

        :return: None

        :raises: CouldNotPerformDBOperation: If the update operation fails.
        """
        self.hashed_otp = data.otp
        self.otp_created_at = data.otp_created_at
        self.last_login_at = data.last_login_at

        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise CouldNotPerformDBOperationException(extra="(User Update Failed)")

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        _id: str,
        data: UserProfileRequest | UserProfileUpdateRequest,
    ) -> None:
        """
        Update a user.

        :param _id: ``(str)``: The unique identifier of the user to update.
        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param data: ``(UpdateBaseUserRequest)``: The data to update a user.

        :return: None

        :raises: CouldNotPerformDBOperation: If the update operation fails.
        """
        stmt = sql_update(cls).where(cls.id == _id).values(**data.model_dump())

        try:
            await session.execute(stmt)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise CouldNotPerformDBOperationException(extra="(User Update Failed)")
