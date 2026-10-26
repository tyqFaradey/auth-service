from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import AuthServiceDep, CurrentUserDep, RefreshRepositoryDep
from config import settings
from schemas.auth import RegisterRequest
from schemas.user import UserResponse

router = APIRouter(prefix="/auth")


def make_responce(access_token: str, refresh_token: str):
    response = JSONResponse(
        content={"access_token": access_token, "token_type": "bearer"}
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # TODO make True
        samesite="lax",
        max_age=int(
            timedelta(days=settings.security.refresh_token_expire).total_seconds()
        ),
    )

    return response


@router.post("/register", response_model=UserResponse)
async def register(
    data: RegisterRequest,
    service: AuthServiceDep,
):
    user = await service.register(data.username, data.email, data.password)

    return user


@router.post("/login")
async def login(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: AuthServiceDep,
):
    access_token, refresh_token = await service.login(
        form.username,
        form.password,
        request.headers.get("x-device-id", "web-app"),
        request.headers.get("user-agent", ""),
        request.client.host,
    )

    response = make_responce(access_token, refresh_token)

    return response


@router.post("/refresh")
async def refresh(service: AuthServiceDep, request: Request):

    old_refresh = request.cookies.get("refresh_token")
    if not old_refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = await service.refresh(
        old_refresh,
        request.headers.get("x-device-id", "web-app"),
        request.client.host,
    )

    response = make_responce(access_token, refresh_token)

    return response


@router.delete("/logout")
async def logout(
    device_id: str | None,
    user_id: CurrentUserDep,
    token_repository: RefreshRepositoryDep,
):
    if device_id:
        await token_repository.delete_by_device(user_id, device_id)
        return {"status": "logged out from device"}
    else:
        await token_repository.delete_all(user_id)
        return {"status": "logged out from all devices"}
