
"""FastAPI dependencies."""

from collections.abc import Generator

from sqlalchemy.orm import Session

from core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for one API request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
