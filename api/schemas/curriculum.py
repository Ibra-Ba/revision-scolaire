
"""Pydantic schemas for the school curriculum."""

from datetime import date, datetime
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



class ChapterCreate(BaseModel):
    """Data required to create a chapter."""

    title: str = Field(min_length=1, max_length=200)
    


class ChapterRead(BaseModel):
    """Chapter data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    subject_id: UUID
    title: str
    position: int
    status: str
    created_at: datetime
    updated_at: datetime


class SubsectionCreate(BaseModel):
    """Data required to create a subsection."""

    title: str = Field(min_length=1, max_length=200)
    lesson_date: date | None = None


class SubsectionRead(BaseModel):
    """Subsection data returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    chapter_id: UUID
    title: str
    position: int
    lesson_date: date | None
    status: str
    created_at: datetime
    updated_at: datetime

