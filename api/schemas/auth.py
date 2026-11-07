
"""Authentication request and response schemas."""

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """Credentials submitted during login."""

    identifier: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    """JWT access token returned after successful login."""

    access_token: str
    token_type: str = "bearer"


class CurrentUserRead(BaseModel):
    """Public information about the authenticated user."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_type: str
    first_name: str
