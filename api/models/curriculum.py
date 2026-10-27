from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (UniqueConstraint("child_id", "name", name="uq_subject_child_name"), CheckConstraint("position > 0", name="ck_subject_position_positive"))

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    child_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("children.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    chapters: Mapped[list["Chapter"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (CheckConstraint("position > 0", name="ck_chapter_position_positive"), CheckConstraint("status IN ('draft','in_progress','completed','archived')", name="ck_chapter_status"))

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    subject_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress", server_default="in_progress")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    subject: Mapped["Subject"] = relationship(back_populates="chapters")
    subsections: Mapped[list["Subsection"]] = relationship(back_populates="chapter", cascade="all, delete-orphan", order_by="Subsection.position")


class Subsection(Base):
    __tablename__ = "subsections"
    __table_args__ = (UniqueConstraint("chapter_id", "position", name="uq_subsection_chapter_position"), CheckConstraint("position > 0", name="ck_subsection_position_positive"), CheckConstraint("status IN ('draft','needs_review','approved','published','rejected')", name="ck_subsection_status"))

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    chapter_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_date: Mapped[date | None] = mapped_column(Date)
    source_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", server_default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    chapter: Mapped["Chapter"] = relationship(back_populates="subsections")
