import datetime as dt
import uuid
from datetime import datetime, timedelta

import jwt

from utils import get_logger

logger = get_logger(__name__)


class Jwt:
    def __init__(
        self,
        access_secret: str,
        refresh_secret: str,
        access_expire_m: int,
        refresh_expire_d: int,
        algorithm: str = "HS256",
    ):
        self.access_secret = access_secret
        self.refresh_secret = refresh_secret
        self.algorithm = algorithm
        self.access_expire_m = access_expire_m
        self.refresh_expire_d = refresh_expire_d
        logger.debug("Jwt initialized: algorithm=%s", algorithm)

    def _create_payload(self, user_id: uuid.UUID, expire: datetime, type: str) -> dict:
        return {
            "sub": str(user_id),
            "exp": expire,
            "type": type,
        }

    def create_tokens(self, user_id: uuid.UUID) -> tuple[str, str]:
        logger.debug("Creating access, refresh token: user_id=%s", user_id)
        access_expire_at = datetime.now(dt.UTC) + timedelta(
            minutes=self.access_expire_m
        )
        refresh_expire_at = datetime.now(dt.UTC) + timedelta(days=self.refresh_expire_d)

        access_token = jwt.encode(
            self._create_payload(user_id, access_expire_at, "access"),
            self.access_secret,
            algorithm=self.algorithm,
        )

        refresh_token = jwt.encode(
            self._create_payload(user_id, refresh_expire_at, "refresh"),
            self.refresh_secret,
            algorithm=self.algorithm,
        )
        logger.debug(
            "Token pair created: user_id=%s access_expires_at=%s refresh_expires_at=%s",
            user_id,
            access_expire_at,
            refresh_expire_at,
        )
        return access_token, refresh_token

    def validate_refresh_token(self, refresh_token: str) -> uuid.UUID | None:
        token = jwt.decode(refresh_token, self.refresh_secret, [self.algorithm])
        if not token:
            return
        return token["sub"]
