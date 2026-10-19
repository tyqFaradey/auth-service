from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from utils import get_logger

logger = get_logger(__name__)


class PasswordHasher:
    def __init__(self, hasher: Argon2PasswordHasher | None = None) -> None:
        self._hasher = hasher if hasher is not None else Argon2PasswordHasher()
        logger.debug("PasswordHasher initialized")

    def hash(self, password: str) -> str:
        logger.debug("Hashing password")
        result = self._hasher.hash(password)
        logger.debug("Password hash generated")
        return result

    def verify(self, password: str, password_hash: str) -> bool:
        logger.debug("Verifying password")
        try:
            result = self._hasher.verify(password_hash, password)
        except (VerificationError, InvalidHashError):
            logger.debug("Password verification failed")
            return False
        logger.debug("Password verified")
        return result
