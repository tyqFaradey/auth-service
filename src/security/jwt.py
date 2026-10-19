import datetime as dt
import uuid
from datetime import datetime, timedelta

import jwt

from utils import get_logger

logger = get_logger(__name__)


class Jwt:
    def __init__(self, secret: str, algorithm: str = "HS256"):
        self.secret = secret
        self.algorithm = algorithm
        logger.debug("Jwt initialized: algorithm=%s", algorithm)

    def create_access_token(self, user_id: uuid.UUID, expires_minutes: int = 20) -> str:
        logger.debug("Creating access token: user_id=%s", user_id)
        expires_at = datetime.now(dt.UTC) + timedelta(minutes=expires_minutes)
        payload = {
            "sub": str(user_id),
            "exp": expires_at,
            "type": "access",
        }
        access_token = jwt.encode(payload, self.secret, algorithm=self.algorithm)
        logger.debug(
            "Access token created: user_id=%s expires_at=%s", user_id, expires_at
        )
        return access_token
