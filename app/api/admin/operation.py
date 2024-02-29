from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database import get_session


class BaseOperation:
    """
    Base class for all operations to load the async session

    :param session: AsyncSession
    """

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self.session = session
