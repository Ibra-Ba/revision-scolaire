
import pytest
from pydantic import ValidationError

from api.schemas.generation import RevisionSheetContent


def valid_revision_sheet() -> dict:
    return {
        "schema_version": "1.0",
        "title": "Les fractions",
        "grade_level": "CM2",
        "subject": "Mathématiques",
        "sections": [
            {
                "title": "Comprendre les fractions",
                "content": "Une fraction représente une partie d'un tout.",
                "key_points": [
                    "Le dénominateur indique le nombre de parts égales.",
                ],
            }
        ],
        "vocabulary": [],
        "examples": [],
        "important_to_remember": [],
    }


def test_valid_revision_sheet_is_accepted() -> None:
    result = RevisionSheetContent.model_validate(valid_revision_sheet())

    assert result.title == "Les fractions"
    assert result.grade_level == "CM2"
    assert len(result.sections) == 1


def test_empty_sections_are_rejected() -> None:
    data = valid_revision_sheet()
    data["sections"] = []

    with pytest.raises(ValidationError):
        RevisionSheetContent.model_validate(data)


def test_empty_required_title_is_rejected() -> None:
    data = valid_revision_sheet()
    data["title"] = "   "

    with pytest.raises(ValidationError):
        RevisionSheetContent.model_validate(data)


def test_unknown_fields_are_rejected() -> None:
    data = valid_revision_sheet()
    data["unexpected_field"] = "unexpected"

    with pytest.raises(ValidationError):
        RevisionSheetContent.model_validate(data)


def test_unsupported_schema_version_is_rejected() -> None:
    data = valid_revision_sheet()
    data["schema_version"] = "2.0"

    with pytest.raises(ValidationError):
        RevisionSheetContent.model_validate(data)
