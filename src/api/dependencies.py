from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import database_manager
from redisdb import redis_manager
from repositories import RefreshTokenRepository, UserRepository
from security import Jwt, PasswordHasher
from services import AuthService


def get_user_repository(session: DbSessionDep) -> UserRepository:
    return UserRepository(session)


def get_refresh_repository(connection: RedisDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(connection)


def get_password_service() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_service() -> Jwt:
    return Jwt(
        access_secret=settings.security.access_secret,
        refresh_secret=settings.security.refresh_secret,
        algorithm=settings.security.algorithm,
        access_expire_m=settings.security.access_token_expire,
        refresh_expire_d=settings.security.refresh_token_expire,
    )


def get_auth_service(
    user_repository: UserRepositoryDep,
    refresh_repository: RefreshRepositoryDep,
    jwt_service: JwtDep,
    password_service: PasswordHasherDep,
) -> AuthService:
    return AuthService(
        user_repository,
        refresh_repository,
        jwt_service,
        password_service,
    )


DbSessionDep = Annotated[AsyncSession, Depends(database_manager.get_session)]
RedisDep = Annotated[Redis, Depends(redis_manager.get_connection)]

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
RefreshRepositoryDep = Annotated[
    RefreshTokenRepository, Depends(get_refresh_repository)
]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_service)]
JwtDep = Annotated[Jwt, Depends(get_jwt_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
