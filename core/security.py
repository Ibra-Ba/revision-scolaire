
"""Security utilities: password hashing and JWT tokens."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password using the recommended Argon2 configuration."""
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its stored hash."""
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: UUID, user_type: str) -> str:
    """Create a signed JWT access token."""
    if user_type not in {"adult", "child"}:
        raise ValueError("Type utilisateur invalide.")

    now = datetime.now(UTC)
    expires_at = now + timedelta(
        minutes=settings.jwt_access_token_expire_minutes
    )

    payload = {
        "sub": str(user_id),
        "type": user_type,
        "iat": now,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={"require": ["sub", "type", "iat", "exp"]},
    )

    if payload["type"] not in {"adult", "child"}:
        raise jwt.InvalidTokenError("Type utilisateur invalide.")

    try:
        UUID(payload["sub"])
    except (ValueError, TypeError) as exc:
        raise jwt.InvalidTokenError("Identifiant utilisateur invalide.") from exc

    return payload
