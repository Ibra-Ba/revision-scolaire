import api.models  # noqa: F401
from core.database import Base


def test_resource_scope_and_type_constraints_exist() -> None:
    constraints = {constraint.name for constraint in Base.metadata.tables["resources"].constraints}
    assert "ck_resource_type" in constraints
    assert "ck_resource_scope" in constraints
    assert "ck_resource_scope_target" in constraints


def test_subsection_position_is_unique_within_chapter() -> None:
    constraints = {constraint.name for constraint in Base.metadata.tables["subsections"].constraints}
    assert "uq_subsection_chapter_position" in constraints
