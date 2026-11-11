
"""Authentication endpoints."""


from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.auth import CurrentUser
from api.dependencies import get_db
from api.models import AdultUser, Child
from api.schemas.auth import ChildLoginRequest, CurrentUserRead, LoginRequest, TokenResponse
from core.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

DbSession = Annotated[Session, Depends(get_db)]


def authenticate_user(
    db: Session,
    identifier: str,
    password: str,
    user_type: str,
    adult_identifier: str | None = None,
) -> AdultUser | Child | None:
    """Authenticate an adult or a child."""

    if user_type == "adult":
        statement = select(AdultUser).where(
            AdultUser.username == identifier
        )

    elif user_type == "child":
        if adult_identifier is None:
            return None

        statement = (
            select(Child)
            .join(AdultUser, Child.adult_user_id == AdultUser.id)
            .where(
                AdultUser.username == adult_identifier,
                AdultUser.is_active.is_(True),
                Child.first_name == identifier,
            )
        )

    else:
        return None

    user = db.scalar(statement)

    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        return None

    return user


def login(
    db: Session,
    credentials: LoginRequest | ChildLoginRequest,
    user_type: str,
) -> TokenResponse:
    """Validate credentials and return an access token."""

    adult_identifier = (
        credentials.adult_identifier
        if isinstance(credentials, ChildLoginRequest)
        else None
    )

    user = authenticate_user(
        db,
        credentials.identifier,
        credentials.password,
        user_type,
        adult_identifier,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.id, user_type)

    return TokenResponse(access_token=token)


@router.post("/adult/login", response_model=TokenResponse)
def adult_login(credentials: LoginRequest, db: DbSession) -> TokenResponse:
    """Log in an adult."""
    return login(db, credentials, "adult")


@router.post("/child/login", response_model=TokenResponse)
def child_login(
    credentials: ChildLoginRequest,
    db: DbSession,
) -> TokenResponse:
    """Log in a child."""
    return login(db, credentials, "child")


@router.get("/me", response_model=CurrentUserRead)
def get_me(user: CurrentUser) -> CurrentUserRead:
    """Return the authenticated user's public profile."""
    user_type = "adult" if isinstance(user, AdultUser) else "child"

    first_name = (
        user.username if isinstance(user, AdultUser) else user.first_name
    )

    return CurrentUserRead(
        id=str(user.id),
        user_type=user_type,
        first_name=first_name,
    )
