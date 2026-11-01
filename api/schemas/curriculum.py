
"""Pydantic schemas for the school curriculum."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    """Data required to create a subject."""

    name: str = Field(min_length=1, max_length=100)
    position: int = Field(default=1, gt=0)


class SubjectRead(BaseModel):
    """Subject data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    child_id: UUID
    name: str
    position: int
    created_at: datetime


class SubjectUpdate(BaseModel):
    """Data accepted when updating a subject."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    position: int | None = Field(default=None, gt=0)
