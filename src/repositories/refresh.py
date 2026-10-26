import datetime as dt
import json
import uuid
from datetime import datetime, timedelta

from redis.asyncio import Redis

from utils.logger import get_logger

logger = get_logger(__name__)


class RefreshTokenRepository:
    def __init__(
        self,
        redis: Redis,
        ttl_days: int = 14,
    ):
        self.redis = redis
        self.ttl = timedelta(days=ttl_days)
        self.ttl_seconds = int(self.ttl.total_seconds())

    def _get_key(self, user_id: uuid.UUID) -> str:
        return f"refresh_tokens:{user_id}"

    async def add(
        self,
        user_id: uuid.UUID,
        device_id: str,
        token: str,
        ip_address: str,
        user_agent: str,
    ) -> None:
        try:
            key = self._get_key(user_id)
            token_data = {
                "token": token,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "created_at": datetime.now(dt.UTC).isoformat(),
            }

            await self.redis.hset(
                key,
                device_id,
                json.dumps(token_data),
            )
            await self.redis.expire(key, self.ttl_seconds)

            logger.info(
                f"Saved refresh token for user_id={user_id}, device_id={device_id}"
            )
        except Exception:
            logger.exception("Failed to save refresh token:")
            raise

    async def get(
        self,
        user_id: uuid.UUID,
        device_id: str,
    ) -> str | None:
        try:
            key = self._get_key(user_id)
            token_data_str = await self.redis.hget(key, device_id)

            if not token_data_str:
                logger.debug(
                    "Token not found for user_id=%s, device_id=%s", user_id, device_id
                )
                return

            token_data = json.loads(token_data_str)
            return token_data["token"]
        except Exception:
            logger.exception(
                "Failed to get refresh token:",
            )
            raise

    async def verify(
        self,
        user_id: uuid.UUID,
        device_id: str,
        token: str,
        ip_address: str | None = None,
    ) -> bool:
        try:
            stored_token = await self.get(user_id, device_id)

            if not stored_token or stored_token != token:
                logger.warning(
                    "Invalid token for user_id=%s, device_id=%s", user_id, device_id
                )
                return False

            # Проверить IP адрес (защита от перехвата токена)
            if ip_address:
                key = self._get_key(user_id)
                token_data_str = await self.redis.hget(key, device_id)

                if token_data_str:
                    token_data = json.loads(token_data_str)
                    if token_data["ip_address"] != ip_address:
                        logger.warning(
                            "IP mismatch for user_id=%s, device_id=%s. "
                            "Expected: %s, Got: %s",
                            user_id,
                            device_id,
                            token_data["ip_address"],
                            ip_address,
                        )
                        return False

            return True
        except Exception:
            logger.exception("Failed to verify token:")
            return False

    async def get_by_device(
        self,
        user_id: uuid.UUID,
        device_id: str,
    ) -> dict | None:
        try:
            key = self._get_key(user_id)
            token_data_str = await self.redis.hget(key, device_id)

            if not token_data_str:
                return None

            return json.loads(token_data_str)
        except Exception:
            logger.exception("Failed to get token by device:")
            raise

    async def get_all_devices(
        self,
        user_id: uuid.UUID,
    ) -> list[dict]:
        try:
            key = self._get_key(user_id)
            devices_raw = await self.redis.hgetall(key)

            devices = []
            for device_id, token_data_str in devices_raw.items():
                token_data = json.loads(token_data_str)
                devices.append(
                    {
                        "device_id": device_id.decode()
                        if isinstance(device_id, bytes)
                        else device_id,
                        "ip_address": token_data["ip_address"],
                        "user_agent": token_data["user_agent"],
                        "created_at": token_data["created_at"],
                    }
                )

            logger.info("Retrieved %s devices for user_id=%s", len(devices), user_id)
            return devices
        except Exception:
            logger.exception("Failed to get all devices")
            raise

    async def delete_by_device(
        self,
        user_id: uuid.UUID,
        device_id: str,
    ) -> bool:
        try:
            key = self._get_key(user_id)
            deleted = await self.redis.hdel(key, device_id)

            if deleted:
                logger.info(
                    "Deleted token for user_id=%s, device_id=%s", user_id, device_id
                )

            return bool(deleted)
        except Exception:
            logger.exception("Failed to delete token by device:")
            raise

    async def delete_all(
        self,
        user_id: uuid.UUID,
    ) -> bool:
        try:
            key = self._get_key(user_id)
            deleted = await self.redis.delete(key)

            logger.info("Deleted all tokens for user_id=%s", user_id)

            return bool(deleted)
        except Exception:
            logger.exception("Failed to delete all tokens:")
            raise

    async def rotate_token(
        self,
        user_id: uuid.UUID,
        device_id: str,
        new_token: str,
    ) -> bool:
        try:
            key = self._get_key(user_id)
            token_data_str = await self.redis.hget(key, device_id)

            if not token_data_str:
                logger.warning(
                    "Cannot rotate token: not found for user_id=%s, device_id=%s",
                    user_id,
                    device_id,
                )
                return False

            token_data = json.loads(token_data_str)
            token_data["token"] = new_token
            token_data["rotated_at"] = datetime.now(dt.UTC).isoformat()

            await self.redis.hset(
                key,
                device_id,
                json.dumps(token_data),
            )
            await self.redis.expire(key, self.ttl_seconds)

            logger.info(
                "Rotated token for user_id=%s, device_id=%s", user_id, device_id
            )
            return True
        except Exception:
            logger.exception("Failed to rotate token:")
            raise

    async def exists(
        self,
        user_id: uuid.UUID,
        device_id: str,
    ) -> bool:
        try:
            key = self._get_key(user_id)
            exists = await self.redis.hexists(key, device_id)
            return bool(exists)
        except Exception:
            logger.exception("Failed to check token existence:")
            raise

    async def count_devices(
        self,
        user_id: uuid.UUID,
    ) -> int:
        try:
            key = self._get_key(user_id)
            count = await self.redis.hlen(key)
            return count
        except Exception:
            logger.exception("Failed to count devices:")
            raise
