
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.models import Chapter, Child, Subject, Subsection


@pytest.fixture
def db_session():
    database_url = os.environ.get("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("TEST_DATABASE_URL n'est pas définie")

    if not database_url.startswith("postgresql"):
        pytest.fail("TEST_DATABASE_URL doit pointer vers PostgreSQL")

    engine = create_engine(database_url)

    try:
        with engine.connect() as connection:
            transaction = connection.begin()
            session = Session(bind=connection)

            try:
                yield session
            finally:
                session.close()
                transaction.rollback()
    finally:
        engine.dispose()


def test_curriculum_hierarchy_persists_in_postgres(db_session: Session) -> None:
    child = Child(
        first_name="Test RéviPote",
        password_hash="test-only-hash",
        grade_level="6e",
    )

    subject = Subject(name="Mathématiques", position=1)
    chapter = Chapter(title="Les fractions", position=1)
    subsection = Subsection(
        title="Comparer des fractions",
        position=1,
        source_text="Deux fractions peuvent être comparées.",
    )

    subject.chapters.append(chapter)
    chapter.subsections.append(subsection)

    # La relation Child -> Subject est portée par child_id.
    db_session.add(child)
    db_session.flush()

    subject.child_id = child.id
    db_session.add(subject)
    db_session.commit()

    child_id = child.id
    subsection_id = subsection.id

    # Expire les objets pour forcer une nouvelle lecture depuis PostgreSQL.
    db_session.expire_all()

    persisted_child = db_session.get(Child, child_id)
    persisted_subsection = db_session.get(Subsection, subsection_id)

    assert persisted_child is not None
    assert persisted_child.first_name == "Test RéviPote"

    assert persisted_subsection is not None
    assert persisted_subsection.title == "Comparer des fractions"
    assert persisted_subsection.chapter.title == "Les fractions"
    assert persisted_subsection.chapter.subject.name == "Mathématiques"
    assert persisted_subsection.chapter.subject.child_id == child_id
