"""Import all ORM models so SQLAlchemy metadata and Alembic can discover them."""

from api.models.accounts import AdultUser, Child
from api.models.curriculum import Chapter, Subject, Subsection
from api.models.learning import ExerciseAttempt, ExerciseSession
from api.models.monitoring import GenerationRun, MonitoringAlert, QualityCheck, SystemMetric
from api.models.resources import (
    Exercise,
    ExerciseSet,
    Resource,
    RevisionSheet,
    resource_subsections,
)
from api.models.reviews import AuditEvent, ResourceReview

__all__ = [
    "AdultUser",
    "AuditEvent",
    "Chapter",
    "Child",
    "Exercise",
    "ExerciseAttempt",
    "ExerciseSession",
    "ExerciseSet",
    "GenerationRun",
    "MonitoringAlert",
    "QualityCheck",
    "Resource",
    "ResourceReview",
    "RevisionSheet",
    "Subject",
    "Subsection",
    "SystemMetric",
    "resource_subsections",
]
