import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Refresh
from utils import get_logger

logger = get_logger(__name__)


class RefreshRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        logger.debug("RefreshRepository initialized")

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            logger.exception("Failed to commit refresh transaction")
            raise
        logger.debug("Refresh transaction committed")

    async def get_by_user_id(self, user_id: uuid.UUID) -> Refresh | None:
        logger.debug("Looking up refresh by user.id: %s", user_id)
        stmt = select(Refresh).where(Refresh.user_id == user_id)
        refresh = await self.session.scalar(stmt)
        logger.debug(
            "Refresh lookup finished: user.id=%s found=%s",
            user_id,
            refresh is not None,
        )
        return refresh

    async def add(
        self, user_id: uuid.UUID, refresh_token: str, auto_commit: bool = True
    ) -> Refresh:
        logger.info("Adding refresh: user.id=%s", user_id)
        refresh = Refresh(
            user_id=user_id,
            refresh_token=refresh_token,
        )
        self.session.add(refresh)
        if auto_commit:
            await self.commit()
        logger.info("Refresh added: user.id=%s", user_id)

        return refresh

    async def delete(self, user_id: uuid.UUID, auto_commit: bool = True) -> None:
        logger.info("Deleting refresh: user.id=%s", user_id)
        existing = await self.get_by_user_id(user_id)

        await self.session.delete(existing)

        if auto_commit:
            await self.commit()

        logger.info("Refresh deleted: user.id=%s", user_id)
