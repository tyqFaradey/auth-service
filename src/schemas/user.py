import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: uuid.UUID

    username: str
    email: EmailStr

    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: datetime | None

    class Config:
        from_attributes = True
