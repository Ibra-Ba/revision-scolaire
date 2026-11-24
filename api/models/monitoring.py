from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.curriculum import SubsectionVersion
from core.database import Base


class GenerationRun(Base):
    __tablename__ = "generation_runs"
    __table_args__ = (
        CheckConstraint("status IN ('queued','running','succeeded','failed','cancelled')", name="ck_generation_run_status"),
        CheckConstraint("estimated_cost_eur IS NULL OR estimated_cost_eur >= 0", name="ck_generation_cost_nonnegative"),
        CheckConstraint("duration_ms IS NULL OR duration_ms >= 0", name="ck_generation_duration_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    subsection_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("subsections.id", ondelete="SET NULL"), index=True)
    operation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    provider: Mapped[str | None] = mapped_column(String(80))
    model_name: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued", server_default="queued", index=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    estimated_cost_eur: Mapped[float | None] = mapped_column(Float)
    error_code: Mapped[str | None] = mapped_column(String(100))
    source_versions: Mapped[list["GenerationRunSubsectionVersion"]] = relationship(
    back_populates="generation_run",
    cascade="all, delete-orphan",
    order_by="GenerationRunSubsectionVersion.position",
)


class QualityCheck(Base):
    __tablename__ = "quality_checks"
    __table_args__ = (CheckConstraint("status IN ('passed','failed','warning','skipped')", name="ck_quality_check_status"),)

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    generation_run_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("generation_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    check_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    details: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str | None] = mapped_column(String(30))
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    labels: Mapped[dict | None] = mapped_column(JSONB)


class MonitoringAlert(Base):
    __tablename__ = "monitoring_alerts"
    __table_args__ = (
        CheckConstraint("severity IN ('info','warning','critical')", name="ck_monitoring_alert_severity"),
        CheckConstraint("status IN ('open','acknowledged','resolved')", name="ck_monitoring_alert_status"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", server_default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))



class GenerationRunSubsectionVersion(Base):
    __tablename__ = "generation_run_subsection_versions"
    __table_args__ = (
        UniqueConstraint(
            "generation_run_id",
            "position",
            name="uq_generation_run_source_position",
        ),
        CheckConstraint(
            "position > 0",
            name="ck_generation_run_source_position_positive",
        ),
    )

    generation_run_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("generation_runs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    subsection_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subsection_versions.id", ondelete="RESTRICT"),
        primary_key=True,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    generation_run: Mapped["GenerationRun"] = relationship(
        back_populates="source_versions"
    )
    subsection_version: Mapped["SubsectionVersion"] = relationship(
        back_populates="generation_usages"
    )
