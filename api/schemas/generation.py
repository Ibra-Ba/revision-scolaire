
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class GenerationSchema(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class RevisionSection(GenerationSchema):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)


class VocabularyItem(GenerationSchema):
    term: str = Field(min_length=1, max_length=150)
    definition: str = Field(min_length=1)


class ExampleItem(GenerationSchema):
    statement: str = Field(min_length=1)
    explanation: str = Field(min_length=1)



class SourceEvidence(GenerationSchema):
    subsection_position: int = Field(gt=0)
    evidence: str = Field(min_length=1)


class EvaluationCriterion(GenerationSchema):
    criterion: str = Field(min_length=1, max_length=300)
    points: int = Field(gt=0)


class ExerciseContent(GenerationSchema):
    position: int = Field(gt=0)
    exercise_type: Literal[
        "multiple_choice",
        "true_false",
        "short_answer",
        "written_response",
    ]
    statement: str = Field(min_length=1)
    points: int = Field(gt=0)

    choices: list[str] | None = None
    expected_answer: str = Field(min_length=1)
    accepted_answers: list[str] = Field(default_factory=list)

    correction: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    reasoning_type: str = Field(min_length=1, max_length=100)

    source_evidence: list[SourceEvidence] = Field(min_length=1)
    evaluation_criteria: list[EvaluationCriterion] | None = None

    @model_validator(mode="after")
    def validate_exercise_type(self) -> "ExerciseContent":
        if self.exercise_type == "multiple_choice":
            if not self.choices or len(self.choices) < 2:
                raise ValueError("A multiple-choice exercise requires at least two choices.")

            if len(set(self.choices)) != len(self.choices):
                raise ValueError("Multiple-choice options must be unique.")

            if self.expected_answer not in self.choices:
                raise ValueError("The expected answer must be one of the choices.")

        elif self.choices is not None:
            raise ValueError("Choices are only allowed for multiple-choice exercises.")

        if (
            self.exercise_type == "true_false"
            and self.expected_answer.lower() not in {"true", "false"}
        ):
            raise ValueError("A true/false answer must be 'true' or 'false'.")
        if self.exercise_type == "written_response":
            if not self.evaluation_criteria:
                raise ValueError("A written response requires evaluation criteria.")

            total_points = sum(
                criterion.points for criterion in self.evaluation_criteria
            )
            if total_points != self.points:
                raise ValueError(
                    "Evaluation criteria points must equal exercise points."
                )

        elif self.evaluation_criteria is not None:
            raise ValueError(
                "Evaluation criteria are only allowed for written responses."
            )

        return self



class RevisionSheetContent(GenerationSchema):
    schema_version: Literal["1.0"]
    title: str = Field(min_length=1, max_length=200)
    grade_level: str = Field(min_length=1, max_length=30)
    subject: str = Field(min_length=1, max_length=100)

    sections: list[RevisionSection] = Field(min_length=1)

    vocabulary: list[VocabularyItem] = Field(default_factory=list)
    examples: list[ExampleItem] = Field(default_factory=list)
    important_to_remember: list[str] = Field(default_factory=list)



class ExerciseSetContent(GenerationSchema):
    schema_version: Literal["1.0"]
    title: str = Field(min_length=1, max_length=200)
    grade_level: str = Field(min_length=1, max_length=30)
    subject: str = Field(min_length=1, max_length=100)
    instructions: str = Field(min_length=1)
    exercises: list[ExerciseContent] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_exercise_positions(self) -> "ExerciseSetContent":
        positions = [exercise.position for exercise in self.exercises]
        expected_positions = list(range(1, len(self.exercises) + 1))

        if sorted(positions) != expected_positions:
            raise ValueError(
                "Exercise positions must be unique and consecutive, starting at 1."
            )

        return self
