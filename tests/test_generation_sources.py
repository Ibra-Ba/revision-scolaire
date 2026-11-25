
import hashlib
from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from api.models import AdultUser, Child
from api.models.curriculum import (
    Chapter,
    Subject,
    Subsection,
    SubsectionVersion,
)
from api.services.generation.sources import get_validated_sources
from core.security import hash_password


@pytest.fixture
def source_adult(db_session: Session) -> AdultUser:
    adult = AdultUser(
        username="generation_sources_adult",
        password_hash=hash_password("AdultPassword123"),
        is_active=True,
    )
    db_session.add(adult)
    db_session.flush()
    return adult


@pytest.fixture
def source_child(
    db_session: Session,
    source_adult: AdultUser,
) -> Child:
    child = Child(
        adult_user_id=source_adult.id,
        first_name="GenerationSourcesChild",
        password_hash=hash_password("ChildPassword123"),
        grade_level="6e",
        is_active=True,
    )
    db_session.add(child)
    db_session.flush()
    return child


@pytest.fixture
def source_subsections(
    db_session: Session,
    source_child: Child,
    source_adult: AdultUser,
) -> list[Subsection]:
    subject = Subject(
        child_id=source_child.id,
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
            validated_by=source_adult.id,
            validator_type="adult",
            validated_at=datetime.now(UTC),
        ),
        Subsection(
            chapter_id=chapter.id,
            title="Additionner des fractions",
            position=2,
            source_text="Pour additionner deux fractions, on utilise un dénominateur commun.",
            status="approved",
            validated_by=source_adult.id,
            validator_type="adult",
            validated_at=datetime.now(UTC),
        ),
    ]
    db_session.add_all(subsections)
    db_session.flush()

    return subsections


def add_version(
    db_session: Session,
    subsection: Subsection,
    adult: AdultUser,
    version_number: int,
    source_text: str,
) -> SubsectionVersion:
    version = SubsectionVersion(
        subsection_id=subsection.id,
        version_number=version_number,
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


def test_get_validated_sources_preserves_requested_order(
    db_session: Session,
    source_child: Child,
    source_adult: AdultUser,
    source_subsections: list[Subsection],
) -> None:
    first, second = source_subsections

    add_version(
        db_session, first, source_adult, 1, first.source_text
    )
    add_version(
        db_session, second, source_adult, 1, second.source_text
    )

    result = get_validated_sources(
        db_session,
        source_child.id,
        [second.id, first.id],
    )

    assert [source.subsection_id for source in result] == [
        second.id,
        first.id,
    ]
    assert [source.position for source in result] == [1, 2]
    assert result[0].source_text == second.source_text
    assert result[1].source_text == first.source_text


def test_get_validated_sources_selects_latest_version(
    db_session: Session,
    source_child: Child,
    source_adult: AdultUser,
    source_subsections: list[Subsection],
) -> None:
    subsection = source_subsections[0]

    add_version(
        db_session,
        subsection,
        source_adult,
        1,
        "Ancien contenu.",
    )
    latest_text = "Contenu validé le plus récent."
    add_version(
        db_session,
        subsection,
        source_adult,
        2,
        latest_text,
    )

    result = get_validated_sources(
        db_session,
        source_child.id,
        [subsection.id],
    )

    assert len(result) == 1
    assert result[0].source_text == latest_text
    assert result[0].subsection_version_id is not None



def test_get_validated_sources_rejects_empty_ids(
    db_session: Session,
    source_child: Child,
) -> None:
    with pytest.raises(ValueError, match="At least one subsection"):
        get_validated_sources(db_session, source_child.id, [])


def test_get_validated_sources_rejects_duplicate_ids(
    db_session: Session,
    source_child: Child,
    source_adult: AdultUser,
    source_subsections: list[Subsection],
) -> None:
    subsection = source_subsections[0]
    add_version(
        db_session,
        subsection,
        source_adult,
        1,
        subsection.source_text,
    )

    with pytest.raises(ValueError, match="Duplicate"):
        get_validated_sources(
            db_session,
            source_child.id,
            [subsection.id, subsection.id],
        )


def test_get_validated_sources_rejects_unknown_subsection(
    db_session: Session,
    source_child: Child,
) -> None:
    unknown_id = UUID("00000000-0000-0000-0000-000000000001")

    with pytest.raises(ValueError, match="not found"):
        get_validated_sources(
            db_session,
            source_child.id,
            [unknown_id],
        )


def test_get_validated_sources_rejects_draft_subsection(
    db_session: Session,
    source_child: Child,
    source_subsections: list[Subsection],
) -> None:
    subsection = source_subsections[0]
    subsection.status = "draft"
    db_session.flush()

    with pytest.raises(ValueError, match="not validated"):
        get_validated_sources(
            db_session,
            source_child.id,
            [subsection.id],
        )


def test_get_validated_sources_rejects_missing_version(
    db_session: Session,
    source_child: Child,
    source_subsections: list[Subsection],
) -> None:
    subsection = source_subsections[0]

    with pytest.raises(ValueError, match="version"):
        get_validated_sources(
            db_session,
            source_child.id,
            [subsection.id],
        )


def test_get_validated_sources_rejects_blank_source_text(
    db_session: Session,
    source_child: Child,
    source_adult: AdultUser,
    source_subsections: list[Subsection],
) -> None:
    subsection = source_subsections[0]
    subsection.source_text = "   "
    db_session.flush()

    add_version(
        db_session,
        subsection,
        source_adult,
        1,
        "   ",
    )

    with pytest.raises(ValueError, match="blank"):
        get_validated_sources(
            db_session,
            source_child.id,
            [subsection.id],
        )



def test_get_validated_sources_rejects_another_child_subsection(
    db_session: Session,
    source_child: Child,
    source_adult: AdultUser,
) -> None:
    other_adult = AdultUser(
        username="generation_sources_other_adult",
        password_hash=hash_password("OtherPassword123"),
        is_active=True,
    )
    db_session.add(other_adult)
    db_session.flush()

    other_child = Child(
        adult_user_id=other_adult.id,
        first_name="OtherGenerationSourcesChild",
        password_hash=hash_password("OtherPassword123"),
        grade_level="CM2",
        is_active=True,
    )
    db_session.add(other_child)
    db_session.flush()

    subject = Subject(
        child_id=other_child.id,
        name="Français",
        position=1,
    )
    db_session.add(subject)
    db_session.flush()

    chapter = Chapter(
        subject_id=subject.id,
        title="Grammaire",
        position=1,
    )
    db_session.add(chapter)
    db_session.flush()

    subsection = Subsection(
        chapter_id=chapter.id,
        title="Les accords",
        position=1,
        source_text="Le verbe s'accorde avec son sujet.",
        status="approved",
        validated_by=other_adult.id,
        validator_type="adult",
        validated_at=datetime.now(UTC),
    )
    db_session.add(subsection)
    db_session.flush()

    add_version(
        db_session,
        subsection,
        other_adult,
        1,
        subsection.source_text,
    )

    with pytest.raises(ValueError, match="not found"):
        get_validated_sources(
            db_session,
            source_child.id,
            [subsection.id],
        )




