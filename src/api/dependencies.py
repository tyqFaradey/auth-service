from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import database_manager
from repositories.user import UserRepository
from security import Jwt, PasswordHasher
from services import AuthService


def get_user_repository(session: DbSessionDep) -> UserRepository:
    return UserRepository(session)


def get_password_service() -> PasswordHasher:
    return PasswordHasher()


def get_jwt_service() -> Jwt:
    return Jwt(settings.security.secret_key, settings.security.algorithm)


def get_auth_service(
    user_repository: UserRepositoryDep,
    jwt_service: JwtDep,
    password_service: PasswordHasherDep,
) -> AuthService:
    return AuthService(
        user_repository,
        jwt_service,
        password_service,
    )


DbSessionDep = Annotated[AsyncSession, Depends(database_manager.get_session)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_service)]
JwtDep = Annotated[Jwt, Depends(get_jwt_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
