from collections.abc import AsyncGenerator

from redis.asyncio import ConnectionPool, Redis

from config import settings
from utils import get_logger

logger = get_logger(__name__)


class RedisManager:
    def __init__(self, url: str, decode_responses: bool = True) -> None:
        logger.debug("RedisManager initialized: decode_responses=%s", decode_responses)
        self.connection_pool: ConnectionPool = ConnectionPool.from_url(
            url=url,
            decode_responses=decode_responses,
            max_connections=50,
        )
        self.redis: Redis = Redis(connection_pool=self.connection_pool)

    async def get_connection(self) -> AsyncGenerator[Redis]:
        logger.debug("Opening Redis connection")
        try:
            await self.redis.ping()
            logger.debug("Redis connection opened")
            yield self.redis
        finally:
            logger.debug("Redis connection closed")

    async def dispose(self) -> None:
        logger.info("Disposing Redis connection pool")
        await self.redis.close()
        logger.info("Redis connection pool disposed")


redis_manager = RedisManager(settings.redis.url)
