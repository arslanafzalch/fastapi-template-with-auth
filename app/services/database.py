from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


class DatabaseSessionManager:
    def __init__(self, host: str, **engine_kwargs):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.connect() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()

        try:
            yield session

        except Exception as e:
            await session.rollback()
            raise

        finally:
            await session.close()


# Modify the connection string for MySQL
sessionmanager = DatabaseSessionManager(
    settings.MYSQL_DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_size=5,
    max_overflow=5,
    pool_timeout=60,
    pool_recycle=3600,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with sessionmanager.session() as session:
        yield session
