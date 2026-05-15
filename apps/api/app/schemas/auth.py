from pydantic import BaseModel

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthUserRead(BaseModel):
    id: int
    email: str
    display_name: str | None
    role: UserRole

    model_config = {"from_attributes": True}
