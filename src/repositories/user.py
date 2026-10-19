from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from utils import get_logger

logger = get_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        logger.debug("UserRepository initialized")

    async def commit(self) -> None:
        try:
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            logger.exception("Failed to commit user transaction")
            raise
        logger.debug("User transaction committed")

    async def get_by_username(self, username: str) -> User | None:
        logger.debug("Looking up user by username: %s", username)
        stmt = select(User).where(User.username == username)
        user = await self.session.scalar(stmt)
        logger.debug(
            "User lookup finished: username=%s found=%s", username, user is not None
        )
        return user

    async def add(
        self, username: str, email: str, password_hash: str, auto_commit: bool = True
    ) -> User:
        logger.info("Adding user: username=%s", username)
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
        )
        self.session.add(user)
        if auto_commit:
            await self.commit()
        logger.info("User added: username=%s", username)

        return user
