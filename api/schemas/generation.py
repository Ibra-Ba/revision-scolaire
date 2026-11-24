
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class RevisionSheetContent(GenerationSchema):
    schema_version: Literal["1.0"]
    title: str = Field(min_length=1, max_length=200)
    grade_level: str = Field(min_length=1, max_length=30)
    subject: str = Field(min_length=1, max_length=100)

    sections: list[RevisionSection] = Field(min_length=1)

    vocabulary: list[VocabularyItem] = Field(default_factory=list)
    examples: list[ExampleItem] = Field(default_factory=list)
    important_to_remember: list[str] = Field(default_factory=list)
