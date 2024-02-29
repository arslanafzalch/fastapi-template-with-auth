from __future__ import annotations

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING, AsyncIterator, Tuple

from sqlalchemy import String, func, TIMESTAMP, select, text, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped, mapped_column, selectinload, load_only

from app.models.base import Base
from .__import_resolves__ import __resolve_base_user_class__

if TYPE_CHECKING:
    from .base_users import BaseUser


class Role(Base):
    __tablename__ = "roles"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Main data fields
    name: Mapped[Optional[str]] = mapped_column(String(25))

    # Relationships
    users: Mapped[List["BaseUser"]] = relationship(back_populates="role")

    # Meta data
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        server_onupdate=func.current_timestamp(),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(server_default=text("true"), nullable=False)

    @classmethod
    async def read_user_roles(cls, session: AsyncSession, user_id: str) -> Role | None:
        """
        Read all roles associated with a user.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param user_id: ``(int)``: The unique identifier of the user to retrieve.

        :return: List[Role] | None: A list of Role objects if found, otherwise None.
        """
        base_user_class = __resolve_base_user_class__()

        stmt = (
            select(cls)
            .join(cls.users)
            .where(base_user_class.id == user_id)
            .options(load_only(cls.id))
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    @classmethod
    async def read(cls, session: AsyncSession, _id: int) -> Role | None:
        """
        Read a role by its unique identifier.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param _id: ``(int)``: The unique identifier of the role to retrieve.

        :return: Role | None: The Role object if found, otherwise None.
        """
        stmt = select(cls).where(cls.id == _id)
        return await session.scalar(stmt)

    @classmethod
    async def read_all(
        cls, session: AsyncSession, include_users: bool = False
    ) -> AsyncIterator[Role]:
        """
        Retrieve all role from the database asynchronously.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param include_users: ``(bool)``: Flag to indicate if associated user should be eagerly loaded. Defaults to False.

        :return: AsyncIterator[Role]: An asynchronous iterator yielding Role objects.
        """
        stmt = select(cls)

        if include_users:
            stmt = stmt.options(selectinload(cls.users))

        stream = await session.stream_scalars(stmt)

        async for row in stream:
            yield row
