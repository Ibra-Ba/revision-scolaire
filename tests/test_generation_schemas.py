
import pytest
from pydantic import ValidationError

from api.schemas.generation import (
    ExerciseContent,
    ExerciseSetContent,
    RevisionSheetContent,
)


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



def valid_multiple_choice() -> dict:
    return {
        "position": 1,
        "exercise_type": "multiple_choice",
        "statement": "Quelle fraction représente trois parts sur quatre ?",
        "points": 1,
        "choices": ["1/4", "2/4", "3/4"],
        "expected_answer": "3/4",
        "accepted_answers": ["3/4"],
        "correction": "La bonne réponse est 3/4.",
        "explanation": "Le numérateur indique le nombre de parts considérées.",
        "reasoning_type": "identification",
        "source_evidence": [
            {
                "subsection_position": 1,
                "evidence": "Le numérateur indique le nombre de parts considérées.",
            }
        ],
    }


def test_valid_multiple_choice_is_accepted() -> None:
    result = ExerciseContent.model_validate(valid_multiple_choice())

    assert result.exercise_type == "multiple_choice"
    assert result.expected_answer == "3/4"
    assert len(result.choices) == 3


def test_multiple_choice_rejects_answer_not_in_choices() -> None:
    data = valid_multiple_choice()
    data["expected_answer"] = "5/4"

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)


def test_multiple_choice_rejects_duplicate_choices() -> None:
    data = valid_multiple_choice()
    data["choices"] = ["1/4", "2/4", "2/4"]

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)



def valid_true_false() -> dict:
    data = valid_multiple_choice()
    data.update(
        {
            "exercise_type": "true_false",
            "statement": "Le dénominateur indique le nombre total de parts égales.",
            "expected_answer": "true",
            "accepted_answers": [],
        }
    )
    data.pop("choices")
    return data


def test_valid_true_false_is_accepted() -> None:
    result = ExerciseContent.model_validate(valid_true_false())

    assert result.exercise_type == "true_false"
    assert result.expected_answer == "true"


def test_true_false_rejects_invalid_answer() -> None:
    data = valid_true_false()
    data["expected_answer"] = "maybe"

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)


def test_true_false_rejects_choices() -> None:
    data = valid_true_false()
    data["choices"] = ["true", "false"]

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)



def valid_short_answer() -> dict:
    data = valid_true_false()
    data.update(
        {
            "exercise_type": "short_answer",
            "statement": "Quel est le rôle du dénominateur ?",
            "expected_answer": "Il indique le nombre total de parts égales.",
            "accepted_answers": [
                "Il indique le nombre de parts égales."
            ],
        }
    )
    return data


def test_valid_short_answer_is_accepted() -> None:
    result = ExerciseContent.model_validate(valid_short_answer())

    assert result.exercise_type == "short_answer"
    assert len(result.accepted_answers) == 1


def test_short_answer_does_not_allow_choices() -> None:
    data = valid_short_answer()
    data["choices"] = ["Réponse A", "Réponse B"]

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)


def test_short_answer_does_not_allow_evaluation_criteria() -> None:
    data = valid_short_answer()
    data["evaluation_criteria"] = [
        {"criterion": "Identifier le dénominateur", "points": 1}
    ]

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)



def valid_written_response() -> dict:
    data = valid_short_answer()
    data.update(
        {
            "exercise_type": "written_response",
            "statement": "Explique pourquoi 2/4 et 1/2 représentent la même quantité.",
            "expected_answer": (
                "Ces deux fractions représentent la même quantité."
            ),
            "accepted_answers": [],
            "points": 3,
            "evaluation_criteria": [
                {
                    "criterion": "Identifier les deux fractions comme équivalentes",
                    "points": 1,
                },
                {
                    "criterion": "Expliquer la simplification de 2/4 en 1/2",
                    "points": 2,
                },
            ],
        }
    )
    return data


def test_valid_written_response_is_accepted() -> None:
    result = ExerciseContent.model_validate(valid_written_response())

    assert result.exercise_type == "written_response"
    assert sum(
        criterion.points for criterion in result.evaluation_criteria
    ) == result.points


def test_written_response_requires_evaluation_criteria() -> None:
    data = valid_written_response()
    data.pop("evaluation_criteria")

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)


def test_written_response_rejects_incorrect_criteria_total() -> None:
    data = valid_written_response()
    data["evaluation_criteria"][0]["points"] = 2

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)


def test_written_response_rejects_zero_criterion_points() -> None:
    data = valid_written_response()
    data["evaluation_criteria"][0]["points"] = 0

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)



def test_exercise_rejects_zero_points() -> None:
    data = valid_short_answer()
    data["points"] = 0

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)


def test_exercise_rejects_zero_position() -> None:
    data = valid_short_answer()
    data["position"] = 0

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)


def test_exercise_requires_source_evidence() -> None:
    data = valid_short_answer()
    data["source_evidence"] = []

    with pytest.raises(ValidationError):
        ExerciseContent.model_validate(data)



def valid_exercise_set() -> dict:
    return {
        "schema_version": "1.0",
        "title": "Les fractions",
        "grade_level": "CM2",
        "subject": "Mathématiques",
        "instructions": "Réponds à toutes les questions.",
        "exercises": [
            valid_short_answer(),
            {
                **valid_true_false(),
                "position": 2,
            },
        ],
    }


def test_valid_exercise_set_is_accepted() -> None:
    result = ExerciseSetContent.model_validate(valid_exercise_set())

    assert result.title == "Les fractions"
    assert len(result.exercises) == 2


def test_exercise_set_rejects_empty_exercises() -> None:
    data = valid_exercise_set()
    data["exercises"] = []

    with pytest.raises(ValidationError):
        ExerciseSetContent.model_validate(data)


def test_exercise_set_rejects_duplicate_positions() -> None:
    data = valid_exercise_set()
    data["exercises"][1]["position"] = 1

    with pytest.raises(ValidationError):
        ExerciseSetContent.model_validate(data)


def test_exercise_set_rejects_missing_position() -> None:
    data = valid_exercise_set()
    data["exercises"][1]["position"] = 3

    with pytest.raises(ValidationError):
        ExerciseSetContent.model_validate(data)


def test_exercise_set_accepts_exercises_in_different_order() -> None:
    data = valid_exercise_set()
    data["exercises"].reverse()

    result = ExerciseSetContent.model_validate(data)

    assert [exercise.position for exercise in result.exercises] == [2, 1]
