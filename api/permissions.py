
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from api.auth import CurrentUser
from api.models import Chapter, Child, Subject, Subsection


def verify_child_access(
    child_id: UUID,
    current_user: CurrentUser,
    db: Session,
) -> Child:
    """Verify that the authenticated user can access a child."""

    child = db.get(Child, child_id)

    if child is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enfant introuvable.",
        )

    if isinstance(current_user, Child):
        if current_user.id != child.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accès interdit à cet enfant.",
            )
    elif child.adult_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit à cet enfant.",
        )

    return child


def verify_subject_access(
    subject_id: UUID,
    current_user: CurrentUser,
    db: Session,
) -> Subject:
    subject = db.get(Subject, subject_id)

    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matière introuvable.",
        )

    verify_child_access(subject.child_id, current_user, db)
    return subject


def verify_chapter_access(
    chapter_id: UUID,
    current_user: CurrentUser,
    db: Session,
) -> Chapter:
    chapter = db.get(Chapter, chapter_id)

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapitre introuvable.",
        )

    verify_subject_access(chapter.subject_id, current_user, db)
    return chapter


def verify_subsection_access(
    subsection_id: UUID,
    current_user: CurrentUser,
    db: Session,
) -> Subsection:
    subsection = db.get(Subsection, subsection_id)

    if subsection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sous-section introuvable.",
        )

    verify_chapter_access(subsection.chapter_id, current_user, db)
    return subsection
