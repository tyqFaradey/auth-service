from fastapi import HTTPException, status

from models import User
from repositories import UserRepository
from security import Jwt, PasswordHasher
from utils import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        jwt_service: Jwt,
        password_service: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.jwt_service = jwt_service
        logger.debug("AuthService initialized")

    async def register(self, username: str, email: str, password: str) -> User:
        logger.info("Registering user: username=%s", username)
        existing_user = await self.user_repository.get_by_username(username)

        if existing_user:
            logger.warning(
                "Registration rejected, user already exists: username=%s", username
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug("Hashing password for registration: username=%s", username)
        hashed_password = self.password_service.hash(password)
        user = await self.user_repository.add(username, email, hashed_password)
        logger.info("User registered: username=%s", username)

        return user

    async def login(self, username: str, password: str) -> str:
        logger.info("Login attempt: username=%s", username)
        user = await self.user_repository.get_by_username(username)

        if not user:
            logger.warning("Login failed, user not found: username=%s", username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug("Creating access token for user: user_id=%s", user.id)
        token = self.jwt_service.create_access_token(user.id)
        logger.info("Login successful: username=%s", username)

        return token
