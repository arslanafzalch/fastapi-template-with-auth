from __future__ import annotations

from typing import AsyncIterator, TypeVar, Any

from sqlalchemy import select, update as sql_update, delete as sql_delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.exceptions import CouldNotPerformDBOperationException

T = TypeVar(
    "T", bound="BaseReadAllMixin"
)  # Specify the bound type for the generic that will ensure the type is a subclass of BaseReadAllMixin


class BaseCRUDMixin:
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs: dict[str, Any]) -> T:
        """
        Create a new instance.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param kwargs: ``(dict)``: Additional keyword arguments.

        :return: T: The created T object.

        :raises: CouldNotPerformDBOperationException: If the creation operation fails.
        :raises: IntegrityError: If the creation operation fails due to an integrity error.
        """
        instance = cls(**kwargs)
        session.add(instance)

        try:
            await session.commit()
            await session.refresh(instance)

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

        return instance

    @classmethod
    async def read(cls, session: AsyncSession, _id: int) -> T | None:
        """
        Read an instance by its unique name.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param _id: ``(int)``: The unique identifier of the instance to retrieve.

        :return: T | None: The T object if found, otherwise None.
        """
        stmt = select(cls).where(cls.id == _id).where(cls.is_active.is_(True))

        return await session.scalar(stmt)

    @classmethod
    async def read_all(cls, session: AsyncSession) -> AsyncIterator[T]:
        """
        Retrieve all field values from the database asynchronously.

        :param session: ``(AsyncSession)``: The asynchronous database session.

        :return: AsyncIterator[T]: An asynchronous iterator yielding T objects.
        """
        stmt = select(cls).where(cls.is_active.is_(True))
        stream = await session.stream(stmt)

        async for row in stream:
            yield row

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        _id: int,
        **kwargs: dict[str, Any],
    ) -> None:
        """
        Update an instance.

        :param _id: ``(int)``: The unique identifier of the user to update.
        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param kwargs: ``(dict)``: Additional keyword arguments.

        :return: None

        :raises: CouldNotPerformDBOperation: If the update operation fails.
        """
        stmt = sql_update(cls).where(cls.id == _id).values(**kwargs)

        try:
            await session.execute(stmt)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise CouldNotPerformDBOperationException(extra="(User Update Failed)")

    @classmethod
    async def delete(cls, session: AsyncSession, _id: int) -> None:
        """
        Delete an instance.

        :param session: ``(AsyncSession)``: The asynchronous database session.
        :param _id: ``(int)``: The unique identifier of the instance to delete.

        :return: None

        :raises: CouldNotPerformDBOperation: If the delete operation fails.
        """
        stmt = sql_delete(cls).where(cls.id == _id)

        try:
            await session.execute(stmt)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise CouldNotPerformDBOperationException(extra="(User Deletion Failed)")
