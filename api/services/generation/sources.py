
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models.curriculum import (
    Chapter,
    Subject,
    Subsection,
    SubsectionVersion,
)


@dataclass(frozen=True, slots=True)
class GenerationSource:
    subsection_id: UUID
    subsection_version_id: UUID
    position: int
    title: str
    source_text: str
    content_hash: str


def get_validated_sources(
    db: Session,
    child_id: UUID,
    subsection_ids: list[UUID],
) -> list[GenerationSource]:
    """Retrieve the latest validated versions of selected subsections."""

    if not subsection_ids:
        raise ValueError("At least one subsection is required.")

    if len(subsection_ids) != len(set(subsection_ids)):
        raise ValueError("Duplicate subsection IDs are not allowed.")

    sources: list[GenerationSource] = []

    for position, subsection_id in enumerate(subsection_ids, start=1):
        subsection = db.scalar(
            select(Subsection)
            .join(Chapter, Subsection.chapter_id == Chapter.id)
            .join(Subject, Chapter.subject_id == Subject.id)
            .where(
                Subsection.id == subsection_id,
                Subject.child_id == child_id,
            )
        )

        if subsection is None:
            raise ValueError(
                f"Subsection not found: {subsection_id}."
            )

        if subsection.status not in {"approved", "published"}:
            raise ValueError(
                f"Subsection is not validated: {subsection_id}."
            )

        version = db.scalar(
            select(SubsectionVersion)
            .where(
                SubsectionVersion.subsection_id == subsection_id
            )
            .order_by(SubsectionVersion.version_number.desc())
            .limit(1)
        )

        if version is None:
            raise ValueError(
                f"No validated version found for subsection: {subsection_id}."
            )

        if not version.source_text or not version.source_text.strip():
            raise ValueError(
                f"Source text is blank for subsection: {subsection_id}."
            )

        sources.append(
            GenerationSource(
                subsection_id=subsection.id,
                subsection_version_id=version.id,
                position=position,
                title=subsection.title,
                source_text=version.source_text,
                content_hash=version.content_hash,
            )
        )

    return sources
