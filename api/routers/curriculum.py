
"""API routes for the school curriculum."""
# ruff: noqa: B008

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.auth import CurrentUser
from api.dependencies import get_db
from api.models import (
    Chapter,
    Child,
    Subject,
    Subsection,
)
from api.models.reviews import AuditEvent
from api.permissions import (
    verify_chapter_access,
    verify_child_access,
    verify_subject_access,
    verify_subsection_access,
)
from api.schemas.curriculum import (
    ChapterCreate,
    ChapterRead,
    SubjectCreate,
    SubjectRead,
    SubsectionContentRead,
    SubsectionContentUpdate,
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
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> Subject:
    """Create a subject for an existing child."""

    if isinstance(current_user, Child):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un adulte peut créer une matière.",
        )

    verify_child_access(child_id, current_user, db)

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
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[Subject]:
    """List subjects belonging to a child."""

    verify_child_access(child_id, current_user, db)

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
def create_chapter(
    subject_id: UUID,
    chapter_data: ChapterCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> Chapter:
    """Create a chapter for an existing subject."""

    if isinstance(current_user, Child):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un adulte peut créer un chapitre.",
        )

    verify_subject_access(subject_id, current_user, db)

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
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[Chapter]:
    """List chapters belonging to a subject."""

    verify_subject_access(subject_id, current_user, db)

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
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> Subsection:
    """Create a subsection in a chapter."""

    if isinstance(current_user, Child):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un adulte peut créer une sous-section.",
        )

    verify_chapter_access(chapter_id, current_user, db)

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
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> list[Subsection]:
    """List subsections of a chapter ordered by position."""

    verify_chapter_access(chapter_id, current_user, db)

    statement = (
        select(Subsection)
        .where(Subsection.chapter_id == chapter_id)
        .order_by(Subsection.position)
    )

    return list(db.scalars(statement).all())


@router.put(
    "/subsections/{subsection_id}/content",
    response_model=SubsectionContentRead,
)
def update_subsection_content(
    subsection_id: UUID,
    content_data: SubsectionContentUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> Subsection:
    """Update the educational content of a subsection."""

    if isinstance(current_user, Child):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un adulte peut modifier le contenu pédagogique.",
        )

    subsection = verify_subsection_access(
        subsection_id,
        current_user,
        db,
    )

    subsection.source_text = content_data.source_text
    subsection.status = "draft"
    subsection.validated_by = None
    subsection.validator_type = None
    subsection.validated_at = None

    try:
        db.commit()
        db.refresh(subsection)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible d'enregistrer le contenu pédagogique.",
        ) from None

    return subsection


@router.get(
    "/subsections/{subsection_id}/content",
    response_model=SubsectionContentRead,
)
def get_subsection_content(
    subsection_id: UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> Subsection:
    """Retrieve the educational content of a subsection."""

    return verify_subsection_access(
        subsection_id,
        current_user,
        db,
    )


@router.post(
    "/subsections/{subsection_id}/validate",
    response_model=SubsectionContentRead,
)
def validate_subsection(
    subsection_id: UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> Subsection:
    """Validate subsection content using the authenticated adult."""

    if isinstance(current_user, Child):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul un adulte peut valider le contenu pédagogique.",
        )

    subsection = verify_subsection_access(
        subsection_id,
        current_user,
        db,
    )

    if not subsection.source_text or not subsection.source_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Le contenu pédagogique est vide.",
        )

    validator_type = "adult"
    validator_id = current_user.id

    subsection.status = "approved"
    subsection.validated_by = validator_id
    subsection.validator_type = validator_type
    subsection.validated_at = datetime.now(UTC)

    audit_event = AuditEvent(
        actor_type=validator_type,
        actor_id=validator_id,
        action="subsection.validated",
        resource_type="subsection",
        resource_id=subsection.id,
        details={
            "validator_type": validator_type,
            "new_status": "approved",
        },
    )

    db.add(audit_event)

    try:
        db.commit()
        db.refresh(subsection)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Impossible d'enregistrer la validation.",
        ) from None

    return subsection