from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class ExerciseSession(Base):
    __tablename__ = "exercise_sessions"
    __table_args__ = (
        CheckConstraint("status IN ('in_progress','completed','abandoned')", name="ck_exercise_session_status"),
        CheckConstraint("score IS NULL OR score >= 0", name="ck_session_score_nonnegative"),
        CheckConstraint("max_score IS NULL OR max_score >= 0", name="ck_session_max_score_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    child_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("children.id", ondelete="RESTRICT"), nullable=False, index=True)
    exercise_set_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("exercise_sets.resource_id", ondelete="RESTRICT"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress", server_default="in_progress")
    score: Mapped[float | None] = mapped_column(Numeric(8, 2))
    max_score: Mapped[float | None] = mapped_column(Numeric(8, 2))
    attempts: Mapped[list["ExerciseAttempt"]] = relationship(back_populates="session", cascade="all, delete-orphan", order_by="ExerciseAttempt.answered_at")


class ExerciseAttempt(Base):
    __tablename__ = "exercise_attempts"
    __table_args__ = (
        UniqueConstraint("session_id", "exercise_id", "attempt_number", name="uq_attempt_session_exercise_number"),
        CheckConstraint("attempt_number > 0", name="ck_attempt_number_positive"),
        CheckConstraint("points_awarded IS NULL OR points_awarded >= 0", name="ck_attempt_points_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("exercise_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False, index=True)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool | None] = mapped_column(nullable=True)
    points_awarded: Mapped[float | None] = mapped_column(Numeric(8, 2))
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    session: Mapped["ExerciseSession"] = relationship(back_populates="attempts")
