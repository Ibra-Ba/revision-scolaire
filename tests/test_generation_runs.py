
import hashlib
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import (
    AdultUser,
    Child,
    GenerationRun,
    GenerationRunSubsectionVersion,
)
from api.models.curriculum import (
    Chapter,
    Subject,
    Subsection,
    SubsectionVersion,
)
from core.security import hash_password


def create_version(
    db_session: Session,
    subsection: Subsection,
    adult: AdultUser,
) -> SubsectionVersion:
    source_text = subsection.source_text

    version = SubsectionVersion(
        subsection_id=subsection.id,
        version_number=1,
        source_text=source_text,
        content_hash=hashlib.sha256(
            source_text.encode("utf-8")
        ).hexdigest(),
        validated_by=adult.id,
        validator_type="adult",
        validated_at=datetime.now(UTC),
    )
    db_session.add(version)
    db_session.flush()
    return version


def create_generation_context(
    db_session: Session,
) -> tuple[AdultUser, Child, list[Subsection]]:
    adult = AdultUser(
        username="generation_runs_adult",
        password_hash=hash_password("AdultPassword123"),
        is_active=True,
    )
    db_session.add(adult)
    db_session.flush()

    child = Child(
        adult_user_id=adult.id,
        first_name="GenerationRunsChild",
        password_hash=hash_password("ChildPassword123"),
        grade_level="6e",
        is_active=True,
    )
    db_session.add(child)
    db_session.flush()

    subject = Subject(
        child_id=child.id,
        name="Mathématiques",
        position=1,
    )
    db_session.add(subject)
    db_session.flush()

    chapter = Chapter(
        subject_id=subject.id,
        title="Les fractions",
        position=1,
    )
    db_session.add(chapter)
    db_session.flush()

    subsections = [
        Subsection(
            chapter_id=chapter.id,
            title="Comparer des fractions",
            position=1,
            source_text="Une moitié est supérieure à un quart.",
            status="approved",
            validated_by=adult.id,
            validator_type="adult",
            validated_at=datetime.now(UTC),
        ),
        Subsection(
            chapter_id=chapter.id,
            title="Additionner des fractions",
            position=2,
            source_text="Pour additionner deux fractions, on utilise un dénominateur commun.",
            status="approved",
            validated_by=adult.id,
            validator_type="adult",
            validated_at=datetime.now(UTC),
        ),
    ]
    db_session.add_all(subsections)
    db_session.flush()

    for subsection in subsections:
        create_version(db_session, subsection, adult)

    return adult, child, subsections


def test_create_generation_run_with_one_source(
    db_session: Session,
) -> None:
    from api.services.generation.runs import create_generation_run
    from api.services.generation.sources import get_validated_sources

    _, child, subsections = create_generation_context(db_session)
    subsection = subsections[0]

    sources = get_validated_sources(
        db_session,
        child.id,
        [subsection.id],
    )

    run = create_generation_run(
        db_session,
        sources,
        operation_type="revision_sheet",
    )

    assert run.id is not None
    assert run.status == "queued"
    assert run.operation_type == "revision_sheet"
    assert run.subsection_id == subsection.id

    associations = db_session.scalars(
        select(GenerationRunSubsectionVersion).where(
            GenerationRunSubsectionVersion.generation_run_id == run.id
        )
    ).all()

    assert len(associations) == 1
    assert associations[0].subsection_version_id == (
        sources[0].subsection_version_id
    )
    assert associations[0].position == 1


def test_create_generation_run_with_multiple_sources(
    db_session: Session,
) -> None:
    from api.services.generation.runs import create_generation_run
    from api.services.generation.sources import get_validated_sources

    _, child, subsections = create_generation_context(db_session)
    first, second = subsections

    sources = get_validated_sources(
        db_session,
        child.id,
        [second.id, first.id],
    )

    run = create_generation_run(
        db_session,
        sources,
        operation_type="exercise_set",
    )

    assert run.status == "queued"
    assert run.operation_type == "exercise_set"
    assert run.subsection_id is None

    associations = db_session.scalars(
        select(GenerationRunSubsectionVersion)
        .where(
            GenerationRunSubsectionVersion.generation_run_id == run.id
        )
        .order_by(GenerationRunSubsectionVersion.position)
    ).all()

    assert len(associations) == 2
    assert associations[0].subsection_version_id == (
        sources[0].subsection_version_id
    )
    assert associations[1].subsection_version_id == (
        sources[1].subsection_version_id
    )
    assert [item.position for item in associations] == [1, 2]



import pytest


def test_create_generation_run_rejects_empty_sources(
    db_session: Session,
) -> None:
    from api.services.generation.runs import create_generation_run

    with pytest.raises(ValueError, match="At least one"):
        create_generation_run(
            db_session,
            [],
            operation_type="revision_sheet",
        )


def test_create_generation_run_rejects_blank_operation_type(
    db_session: Session,
) -> None:
    from api.services.generation.runs import create_generation_run

    _, child, subsections = create_generation_context(db_session)

    from api.services.generation.sources import get_validated_sources

    sources = get_validated_sources(
        db_session,
        child.id,
        [subsections[0].id],
    )

    with pytest.raises(ValueError, match="Operation type"):
        create_generation_run(
            db_session,
            sources,
            operation_type="   ",
        )


def test_create_generation_run_does_not_commit_transaction(
    db_session: Session,
) -> None:
    from api.services.generation.runs import create_generation_run
    from api.services.generation.sources import get_validated_sources

    _, child, subsections = create_generation_context(db_session)

    sources = get_validated_sources(
        db_session,
        child.id,
        [subsections[0].id],
    )

    run = create_generation_run(
        db_session,
        sources,
        operation_type="revision_sheet",
    )

    run_id = run.id
    db_session.rollback()

    persisted_run = db_session.get(GenerationRun, run_id)
    assert persisted_run is None

