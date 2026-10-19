from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import AuthServiceDep
from schemas.auth import AuthResponce, RegisterRequest
from schemas.user import UserResponse

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    service: AuthServiceDep,
):
    user = await service.register(data.username, data.email, data.password)

    return user


@router.post("/login", response_model=AuthResponce)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
):
    token = await service.login(form.username, form.password)
    return AuthResponce(access_token=token, refresh_token="")
