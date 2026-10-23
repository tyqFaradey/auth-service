from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import AuthServiceDep
from config import settings
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


@router.post("/login")
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
):
    access_token, refresh_token = await service.login(form.username, form.password)

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # TODO make True
        samesite="lax",
        max_age=settings.security.refresh_token_expire * 24 * 60 * 60,
    )

    return response


@router.post("/refresh")
async def refresh(service: AuthServiceDep, request: Request):

    access_token, refresh_token = await service.refresh(request)

    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # TODO make True
        samesite="lax",
        max_age=settings.security.refresh_token_expire * 24 * 60 * 60,
    )

    return response
