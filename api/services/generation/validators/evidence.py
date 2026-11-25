
from api.schemas.generation import ExerciseSetContent


def validate_exercise_set_evidence(
    exercise_set: ExerciseSetContent,
    source_texts: dict[int, str],
) -> None:
    """Validate that every exercise evidence is an exact source excerpt."""
    if not source_texts:
        raise ValueError("At least one source text is required.")

    for exercise in exercise_set.exercises:
        for evidence in exercise.source_evidence:
            source_text = source_texts.get(evidence.subsection_position)

            if source_text is None:
                raise ValueError(
                    f"Unknown source position: {evidence.subsection_position}."
                )

            if evidence.evidence not in source_text:
                raise ValueError(
                    "Evidence does not match its source text "
                    f"(source position: {evidence.subsection_position})."
                )
