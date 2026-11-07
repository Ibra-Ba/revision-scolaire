
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.main import app
from api.models import (
    AdultUser,
    AuditEvent,
    Child,
)
from api.models.curriculum import Chapter, Subject, Subsection
from core.security import hash_password


@pytest.fixture
def client(db_session: Session):
    """Create a FastAPI test client using the isolated test database."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)

@pytest.fixture
def test_adult(db_session: Session) -> AdultUser:
    adult = AdultUser(
        username="auth_test_adult",
        password_hash=hash_password("AdultPassword123"),
        is_active=True,
    )
    db_session.add(adult)
    db_session.flush()
    return adult


@pytest.fixture
def other_adult(db_session: Session) -> AdultUser:
    adult = AdultUser(
        username="other_test_adult",
        password_hash=hash_password("OtherAdultPassword123"),
        is_active=True,
    )
    db_session.add(adult)
    db_session.flush()
    return adult


@pytest.fixture
def test_child(
    db_session: Session,
    test_adult: AdultUser,
    ) -> Child:
    child = Child(
        adult_user_id=test_adult.id,
        first_name="AuthTestChild",
        password_hash=hash_password("ChildPassword123"),
        grade_level="6e",
        is_active=True,
    )
    db_session.add(child)
    db_session.flush()
    return child


def test_adult_login_success(client, test_adult):
    response = client.post(
        "/auth/adult/login",
        json={
            "identifier": test_adult.username,
            "password": "AdultPassword123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_child_login_success(client, test_child):
    response = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_adult_login_wrong_password(client, test_adult):
    response = client.post(
        "/auth/adult/login",
        json={
            "identifier": test_adult.username,
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


def test_child_login_wrong_password(client, test_child):
    response = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "WrongPassword123",
        },
    )

    assert response.status_code == 401


def test_adult_can_read_own_profile(client, test_adult):
    login = client.post(
        "/auth/adult/login",
        json={
            "identifier": test_adult.username,
            "password": "AdultPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["user_type"] == "adult"
    assert response.json()["id"] == str(test_adult.id)


def test_child_can_read_own_profile(client, test_child):
    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["user_type"] == "child"
    assert response.json()["id"] == str(test_child.id)


def test_profile_requires_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


@pytest.fixture
def test_subject(db_session: Session, test_child: Child) -> Subject:
    subject = Subject(
        child_id=test_child.id,
        name="Mathématiques",
        position=1,
    )
    db_session.add(subject)
    db_session.flush()
    return subject



def test_child_cannot_create_subject(client, test_child):
    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.post(
        f"/children/{test_child.id}/subjects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Français", "position": 1},
    )

    assert response.status_code == 403


def test_child_can_list_own_subjects(client, test_child, test_subject):
    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.get(
        f"/children/{test_child.id}/subjects",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Mathématiques"


def test_child_cannot_list_another_child_subjects(
    client, test_child, other_adult, db_session
):
    other_child = Child(
        first_name="OtherTestChild",
        password_hash=hash_password("OtherPassword123"),
        grade_level="CM2",
        is_active=True,
        adult_user_id=other_adult.id,
    )
    db_session.add(other_child)
    db_session.flush()

    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.get(
        f"/children/{other_child.id}/subjects",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_child_cannot_create_chapter(client, test_child, test_subject):
    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.post(
        f"/subjects/{test_subject.id}/chapters",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Les fractions"},
    )

    assert response.status_code == 403


@pytest.fixture
def test_other_child_subject(
    db_session: Session,
    other_adult: AdultUser,
) -> Subject:
    other_child = Child(
        first_name="OtherTestChild",
        password_hash=hash_password("OtherPassword123"),
        grade_level="CM2",
        is_active=True,
        adult_user_id=other_adult.id,
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

    return subject


def test_child_cannot_list_another_child_chapters(
    client, test_child, test_other_child_subject
):
    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.get(
        f"/subjects/{test_other_child_subject.id}/chapters",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


@pytest.fixture
def test_other_child_chapter(
    db_session: Session,
    test_other_child_subject: Subject,
) -> Chapter:
    chapter = Chapter(
        subject_id=test_other_child_subject.id,
        title="Grammaire",
        position=1,
    )
    db_session.add(chapter)
    db_session.flush()
    return chapter


def test_child_cannot_create_subsection(
    client, test_child, test_other_child_chapter
):
    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.post(
        f"/chapters/{test_other_child_chapter.id}/subsections",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Les accords"},
    )

    assert response.status_code == 403


def test_child_cannot_read_another_child_subsection(
    client, test_child, test_other_child_chapter, db_session
):
    subsection = Subsection(
        chapter_id=test_other_child_chapter.id,
        title="Les accords",
        position=1,
        source_text="Le verbe s'accorde avec son sujet.",
    )
    db_session.add(subsection)
    db_session.flush()

    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.get(
        f"/subsections/{subsection.id}/content",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_child_cannot_update_subsection_content(
    client, test_child, test_subject, db_session
):
    chapter = Chapter(
        subject_id=test_subject.id,
        title="Les fractions",
        position=1,
    )
    db_session.add(chapter)
    db_session.flush()

    subsection = Subsection(
        chapter_id=chapter.id,
        title="Comparer des fractions",
        position=1,
        source_text="Contenu initial.",
    )
    db_session.add(subsection)
    db_session.flush()

    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.put(
        f"/subsections/{subsection.id}/content",
        headers={"Authorization": f"Bearer {token}"},
        json={"source_text": "Contenu modifié par un enfant."},
    )

    assert response.status_code == 403



def test_adult_can_validate_subsection_with_own_identity(
    client, test_adult, test_child, test_subject, db_session
):
    chapter = Chapter(
        subject_id=test_subject.id,
        title="Les fractions",
        position=1,
    )
    db_session.add(chapter)
    db_session.flush()

    subsection = Subsection(
        chapter_id=chapter.id,
        title="Comparer des fractions",
        position=1,
        source_text="Une moitié est supérieure à un quart.",
    )
    db_session.add(subsection)
    db_session.flush()

    login = client.post(
        "/auth/adult/login",
        json={
            "identifier": test_adult.username,
            "password": "AdultPassword123",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.post(
        f"/subsections/{subsection.id}/validate",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "approved"
    assert data["validated_by"] == str(test_adult.id)
    assert data["validator_type"] == "adult"
    assert data["validated_at"] is not None
    audit_event = (
    db_session.query(AuditEvent)
    .filter_by(
        resource_id=subsection.id,
        action="subsection.validated",
        )
    .one()
    )

    assert audit_event.actor_type == "adult"
    assert audit_event.actor_id == test_adult.id
    assert audit_event.resource_type == "subsection"


def test_child_cannot_validate_another_child_subsection(
    client, test_child, test_other_child_chapter, db_session
):
    subsection = Subsection(
        chapter_id=test_other_child_chapter.id,
        title="Les accords",
        position=1,
        source_text="Le verbe s'accorde avec son sujet.",
    )
    db_session.add(subsection)
    db_session.flush()

    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.post(
        f"/subsections/{subsection.id}/validate",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_child_cannot_spoof_validator_identity(
    client,
    test_child,
    test_subject,
    db_session,
):
    chapter = Chapter(
        subject_id=test_subject.id,
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
    )
    db_session.add(subsection)
    db_session.flush()

    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]

    response = client.post(
        f"/subsections/{subsection.id}/validate",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Seul un adulte peut valider le contenu pédagogique."
    )

    db_session.refresh(subsection)
    assert subsection.status == "draft"

def test_list_subsections_requires_authentication(
    client, test_other_child_chapter, db_session
):
    subsection = Subsection(
        chapter_id=test_other_child_chapter.id,
        title="Contenu confidentiel",
        position=1,
        source_text="Contenu pédagogique réservé.",
    )
    db_session.add(subsection)
    db_session.flush()

    response = client.get(
        f"/chapters/{test_other_child_chapter.id}/subsections"
    )

    assert response.status_code == 401

def test_child_cannot_list_another_child_subsections(
    client, test_child, test_other_child_chapter, db_session
):
    subsection = Subsection(
        chapter_id=test_other_child_chapter.id,
        title="Sous-section privée",
        position=1,
        source_text="Contenu réservé à un autre enfant.",
    )
    db_session.add(subsection)
    db_session.flush()

    login = client.post(
    "/auth/child/login",
    json={
        "identifier": test_child.first_name,
        "password": "ChildPassword123",
    },
)
    token = login.json()["access_token"]

    response = client.get(
        f"/chapters/{test_other_child_chapter.id}/subsections",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_child_can_list_own_subsections(
    client, test_child, test_subject, db_session
):
    chapter = Chapter(
        subject_id=test_subject.id,
        title="Grammaire",
        position=1,
    )
    db_session.add(chapter)
    db_session.flush()

    subsection = Subsection(
        chapter_id=chapter.id,
        title="Les noms",
        position=1,
        source_text="Le nom désigne une personne, un animal ou une chose.",
    )
    db_session.add(subsection)
    db_session.flush()

    login = client.post(
        "/auth/child/login",
        json={
            "identifier": test_child.first_name,
            "password": "ChildPassword123",
        },
    )
    token = login.json()["access_token"]

    response = client.get(
        f"/chapters/{chapter.id}/subsections",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Les noms"


def test_parent_can_access_own_child(
    test_adult, test_child, db_session
):
    from api.permissions import verify_child_access

    child = verify_child_access(
        test_child.id,
        test_adult,
        db_session,
    )

    assert child.id == test_child.id


def test_parent_cannot_access_another_family_child(
    test_adult,
    test_other_child_subject,
    db_session,
):
    from api.permissions import verify_child_access

    with pytest.raises(HTTPException) as exc_info:
        verify_child_access(
            test_other_child_subject.child_id,
            test_adult,
            db_session,
        )

    assert exc_info.value.status_code == 403