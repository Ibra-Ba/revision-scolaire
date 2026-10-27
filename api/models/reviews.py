from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


class ResourceReview(Base):
    __tablename__ = "resource_reviews"
    __table_args__ = (
        CheckConstraint("status IN ('pending','approved','rejected','changes_requested')", name="ck_resource_review_status"),
        CheckConstraint("reason IS NULL OR length(reason) <= 500", name="ck_resource_review_reason_length"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    resource_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending", server_default="pending", index=True)
    reason: Mapped[str | None] = mapped_column(String(500))
    reviewed_by: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("adult_users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(50))
    resource_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
