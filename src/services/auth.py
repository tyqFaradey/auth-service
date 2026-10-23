from fastapi import HTTPException, Request, status

from models import User
from repositories import RefreshRepository, UserRepository
from security import Jwt, PasswordHasher
from utils import get_logger

logger = get_logger(__name__)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        refresh_repository: RefreshRepository,
        jwt_service: Jwt,
        password_service: PasswordHasher,
    ):
        self.user_repository = user_repository
        self.refresh_repository = refresh_repository
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

    async def login(self, username: str, password: str) -> tuple[str, str]:
        logger.info("Login attempt: username=%s", username)
        user = await self.user_repository.get_by_username(username)

        if not user or not self.password_service.verify(password, user.password_hash):
            logger.warning("Login failed, user not found: username=%s", username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug("Creating token pair for user: user_id=%s", user.id)
        access_token, refresh_token = self.jwt_service.create_tokens(user.id)
        await self.refresh_repository.add(user.id, refresh_token)

        logger.info("Login successful: username=%s", username)

        return access_token, refresh_token

    async def refresh(self, request: Request) -> tuple[str, str]:
        refresh_token = request.cookies.get("refresh_token")

        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = self.jwt_service.validate_refresh_token(refresh_token)

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not valid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        stored = await self.refresh_repository.get_by_user_id(user_id)

        if not stored:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not valid",
                headers={"WWW-Authenticate": "Bearer"},
            )

        await self.refresh_repository.delete(user_id)

        logger.debug("Creating token pair for user: user_id=%s", user_id)
        access_token, refresh_token = self.jwt_service.create_tokens(user_id)

        await self.refresh_repository.add(user_id, refresh_token)

        logger.debug("Refresh tokens successful: user.id=%s", user_id)

        return access_token, refresh_token
