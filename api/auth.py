
"""Authentication dependencies for FastAPI."""

from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models import AdultUser, Child
from core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> AdultUser | Child:
    """Retrieve the authenticated and active user from the JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentification invalide ou expirée.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise credentials_exception
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = UUID(payload["sub"])
        user_type = payload["type"]
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise credentials_exception from None

    if user_type == "adult":
        user = db.get(AdultUser, user_id)
    elif user_type == "child":
        user = db.get(Child, user_id)
    else:
        raise credentials_exception

    if user is None or not user.is_active:
        raise credentials_exception

    return user


CurrentUser = Annotated[AdultUser | Child, Depends(get_current_user)]
