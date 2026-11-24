import api.models  # noqa: F401
from core.database import Base


def test_expected_tables_are_registered() -> None:
    expected = {
    "adult_users", "children", "subjects", "chapters", "subsections",
    "subsection_versions",
    "resources", "revision_sheets", "exercise_sets", "resource_subsections",
    "exercises", "exercise_sessions", "exercise_attempts", "resource_reviews",
    "audit_events", "generation_runs", "quality_checks", "system_metrics",
    "monitoring_alerts", "generation_run_subsection_versions",
    }
    assert expected == set(Base.metadata.tables)


def test_resource_subsections_has_composite_primary_key() -> None:
    table = Base.metadata.tables["resource_subsections"]
    assert {column.name for column in table.primary_key.columns} == {"resource_id", "subsection_id"}


def test_generation_run_subsection_versions_has_composite_primary_key() -> None:
    table = Base.metadata.tables["generation_run_subsection_versions"]

    assert {
        column.name for column in table.primary_key.columns
    } == {"generation_run_id", "subsection_version_id"}