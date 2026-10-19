from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings
from utils import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    def __init__(self, url: str, echo: bool = False) -> None:
        logger.debug("DatabaseManager initialized: echo=%s", echo)
        self.engine: AsyncEngine = create_async_engine(
            url=url, echo=echo, pool_pre_ping=True
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        logger.debug("Opening database session")
        async with self.session_factory() as session:
            logger.debug("Database session opened")
            yield session
            logger.debug("Database session closed")

    async def dispose(self) -> None:
        logger.info("Disposing database engine")
        await self.engine.dispose()
        logger.info("Database engine disposed")


database_manager = DatabaseManager(settings.database.url)
