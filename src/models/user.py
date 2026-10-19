import datetime
from datetime import datetime as dt

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)

    password_hash: Mapped[str] = mapped_column(nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    is_verified: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True), default=dt.now(datetime.UTC)
    )
    updated_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True),
        default=dt.now(datetime.UTC),
        onupdate=dt.now(datetime.UTC),
    )
    last_login: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=True)
    