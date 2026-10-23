import datetime
import uuid
from datetime import datetime as dt

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Refresh(Base):
    __tablename__ = "refreshes"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), index=True)

    refresh_token: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True), default=dt.now(datetime.UTC)
    )
