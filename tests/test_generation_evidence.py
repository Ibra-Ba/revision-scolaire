
import pytest

from api.schemas.generation import ExerciseSetContent
from api.services.generation.validators.evidence import (
    validate_exercise_set_evidence,
)


def valid_exercise_set() -> ExerciseSetContent:
    return ExerciseSetContent.model_validate(
        {
            "schema_version": "1.0",
            "title": "Les fractions",
            "grade_level": "CM2",
            "subject": "Mathématiques",
            "instructions": "Réponds aux questions.",
            "exercises": [
                {
                    "position": 1,
                    "exercise_type": "short_answer",
                    "statement": "Quel est le rôle du dénominateur ?",
                    "points": 1,
                    "expected_answer": "Il indique le nombre de parts égales.",
                    "accepted_answers": [],
                    "correction": "Le dénominateur indique le nombre de parts égales.",
                    "explanation": "Il indique le nombre total de parts égales.",
                    "reasoning_type": "identification",
                    "source_evidence": [
                        {
                            "subsection_position": 1,
                            "evidence": "Le dénominateur indique le nombre total de parts égales.",
                        }
                    ],
                }
            ],
        }
    )


def test_exact_source_evidence_is_accepted() -> None:
    exercise_set = valid_exercise_set()
    source_texts = {
        1: "Une fraction représente un tout. Le dénominateur indique le nombre total de parts égales."
    }

    validate_exercise_set_evidence(exercise_set, source_texts)


def test_reformulated_evidence_is_rejected() -> None:
    exercise_set = valid_exercise_set()
    source_texts = {
        1: "Le dénominateur représente le nombre total de parts égales."
    }

    with pytest.raises(ValueError, match="does not match"):
        validate_exercise_set_evidence(exercise_set, source_texts)


def test_unknown_source_position_is_rejected() -> None:
    exercise_set = valid_exercise_set()

    with pytest.raises(ValueError, match="Unknown source position"):
        validate_exercise_set_evidence(exercise_set, {2: "Un autre cours."})


def test_empty_source_mapping_is_rejected() -> None:
    with pytest.raises(ValueError, match="At least one source"):
        validate_exercise_set_evidence(valid_exercise_set(), {})
