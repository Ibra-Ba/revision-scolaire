
"""API routes for the school curriculum."""
# ruff: noqa: B008

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models import Chapter, Child, Subject
from api.models.curriculum import Subsection
from api.schemas.curriculum import (
    ChapterCreate,
    ChapterRead,
    SubjectCreate,
    SubjectRead,
    SubsectionCreate,
    SubsectionRead,
)

router = APIRouter(tags=["Curriculum"])


@router.post(
    "/children/{child_id}/subjects",
    response_model=SubjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_subject(
    child_id: UUID,
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
) -> Subject:
    """Create a subject for an existing child."""

    child = db.get(Child, child_id)
    if child is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enfant introuvable.",
        )

    subject = Subject(
        child_id=child_id,
        name=subject_data.name,
        position=subject_data.position,
    )

    try:
        db.add(subject)
        db.commit()
        db.refresh(subject)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cette matière existe déjà pour cet enfant.",
        ) from exc

    return subject


@router.get(
    "/children/{child_id}/subjects",
    response_model=list[SubjectRead],
)
def list_subjects(
    child_id: UUID,
    db: Session = Depends(get_db),
) -> list[Subject]:
    """List subjects belonging to a child."""

    child = db.get(Child, child_id)
    if child is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enfant introuvable.",
        )

    statement = (
        select(Subject)
        .where(Subject.child_id == child_id)
        .order_by(Subject.position, Subject.name)
    )

    return list(db.scalars(statement).all())


@router.post(
    "/subjects/{subject_id}/chapters",
    response_model=ChapterRead,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/subjects/{subject_id}/chapters",
    response_model=ChapterRead,
    status_code=status.HTTP_201_CREATED,
)
def create_chapter(
    subject_id: UUID,
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db),
) -> Chapter:
    """Create a chapter for an existing subject."""

    subject = db.get(Subject, subject_id)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière introuvable.",
        )

    max_position = db.scalar(
        select(func.max(Chapter.position)).where(
            Chapter.subject_id == subject_id
        )
    )

    next_position = (max_position or 0) + 1

    chapter = Chapter(
        subject_id=subject_id,
        title=chapter_data.title,
        position=next_position,
    )

    try:
        db.add(chapter)
        db.commit()
        db.refresh(chapter)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Position de chapitre déjà utilisée pour cette matière.",
        ) from exc

    return chapter

@router.get(
    "/subjects/{subject_id}/chapters",
    response_model=list[ChapterRead],
)
def list_chapters(
    subject_id: UUID,
    db: Session = Depends(get_db),
) -> list[Chapter]:
    """List chapters belonging to a subject."""

    subject = db.get(Subject, subject_id)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière introuvable.",
        )

    statement = (
        select(Chapter)
        .where(Chapter.subject_id == subject_id)
        .order_by(Chapter.position, Chapter.title)
    )

    return list(db.scalars(statement).all())

@router.post(
    "/chapters/{chapter_id}/subsections",
    response_model=SubsectionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_subsection(
    chapter_id: UUID,
    subsection_data: SubsectionCreate,
    db: Session = Depends(get_db),
) -> Subsection:
    """Create a subsection in a chapter."""
    chapter = db.get(Chapter, chapter_id)

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre introuvable.",
        )

    max_position = db.scalar(
        select(func.max(Subsection.position)).where(
            Subsection.chapter_id == chapter_id
        )
    )
    next_position = (max_position or 0) + 1

    subsection = Subsection(
        chapter_id=chapter_id,
        title=subsection_data.title,
        position=next_position,
        lesson_date=subsection_data.lesson_date,
    )

    db.add(subsection)

    try:
        db.commit()
        db.refresh(subsection)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Position de sous-section déjà utilisée dans ce chapitre.",
        ) from None

    return subsection

@router.get(
    "/chapters/{chapter_id}/subsections",
    response_model=list[SubsectionRead],
)
def list_subsections(
    chapter_id: UUID,
    db: Session = Depends(get_db),
) -> list[Subsection]:
    """List subsections of a chapter ordered by position."""
    chapter = db.get(Chapter, chapter_id)

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre introuvable.",
        )

    statement = (
        select(Subsection)
        .where(Subsection.chapter_id == chapter_id)
        .order_by(Subsection.position)
    )

    return list(db.scalars(statement).all())