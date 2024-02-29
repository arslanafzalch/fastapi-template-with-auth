from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, func, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import (
    relationship,
    Mapped,
    mapped_column,
)

from app.models.base import Base
from app.models.roles import Role


class BaseUser(Base):
    """
    Table used to store the base user data.
    """

    __tablename__ = "base_users"

    # Primary Key
    id: Mapped[str] = mapped_column(String(50), primary_key=True)

    # Main data fields
    username: Mapped[str] = mapped_column(String(50), index=True, unique=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_otp: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    user_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Foreign Keys
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True
    )

    # Relationships
    role: Mapped["Role"] = relationship(back_populates="users", lazy="noload")

    # Meta data
    last_login_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=True
    )
    otp_created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False),
        server_default=func.now(),
        server_onupdate=func.current_timestamp(),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=False), server_default=func.now()
    )

    is_active: Mapped[bool] = mapped_column(server_default=text("true"), nullable=False)

    __mapper_args__ = {"polymorphic_on": user_type}
