from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from api.models.curriculum import Chapter, Subsection

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base

resource_subsections = Table(
    "resource_subsections",
    Base.metadata,
    Column("resource_id", PG_UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True),
    Column("subsection_id", PG_UUID(as_uuid=True), ForeignKey("subsections.id", ondelete="RESTRICT"), primary_key=True),
    Column("position", Integer, nullable=False, default=1, server_default="1"),
    CheckConstraint("position > 0", name="ck_resource_subsection_position_positive"),
)


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = (
        CheckConstraint("resource_type IN ('revision_sheet','exercise_set')", name="ck_resource_type"),
        CheckConstraint("scope IN ('chapter','subsections')", name="ck_resource_scope"),
        CheckConstraint("status IN ('draft','needs_review','approved','published','rejected')", name="ck_resource_status"),
        CheckConstraint("version > 0", name="ck_resource_version_positive"),
        CheckConstraint("(scope = 'chapter' AND chapter_id IS NOT NULL) OR (scope = 'subsections' AND chapter_id IS NULL)", name="ck_resource_scope_target"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)
    scope: Mapped[str] = mapped_column(String(20), nullable=False)
    chapter_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="RESTRICT"), index=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", server_default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    created_by_type: Mapped[str | None] = mapped_column(String(20))
    subsections: Mapped[list[Subsection]] = relationship(secondary=resource_subsections, lazy="selectin") 
    chapter: Mapped[Chapter | None] = relationship() 
    __mapper_args__: ClassVar[dict[str, object]] = {
    "polymorphic_on": resource_type,
    "polymorphic_abstract": True,
}


class RevisionSheet(Resource):
    __tablename__ = "revision_sheets"

    resource_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    __mapper_args__ = {"polymorphic_identity": "revision_sheet"}  # noqa: RUF012


class ExerciseSet(Resource):
    __tablename__ = "exercise_sets"

    resource_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    exercises: Mapped[list[Exercise]] = relationship(back_populates="exercise_set", cascade="all, delete-orphan", order_by="Exercise.position")
    __mapper_args__ = {"polymorphic_identity": "exercise_set"}  # noqa: RUF012


class Exercise(Base):
    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint("exercise_set_id", "position", name="uq_exercise_set_position"),
        CheckConstraint("position > 0", name="ck_exercise_position_positive"),
        CheckConstraint("points >= 0", name="ck_exercise_points_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    exercise_set_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("exercise_sets.resource_id", ondelete="CASCADE"), nullable=False, index=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    exercise_type: Mapped[str] = mapped_column(String(40), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[str] = mapped_column(Text, nullable=False)
    accepted_answers: Mapped[list | None] = mapped_column(JSONB)
    correction: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    exercise_set: Mapped[ExerciseSet] = relationship(back_populates="exercises")
    