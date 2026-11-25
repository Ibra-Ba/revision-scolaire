

from sqlalchemy.orm import Session

from api.models import GenerationRun, GenerationRunSubsectionVersion
from api.services.generation.sources import GenerationSource


def create_generation_run(
    db: Session,
    sources: list[GenerationSource],
    operation_type: str,
) -> GenerationRun:
    """Create a queued generation run and associate its source versions."""

    if not sources:
        raise ValueError("At least one generation source is required.")

    if not operation_type.strip():
        raise ValueError("Operation type cannot be blank.")

    subsection_ids = {source.subsection_id for source in sources}

    run = GenerationRun(
        subsection_id=(
            next(iter(subsection_ids)) if len(subsection_ids) == 1 else None
        ),
        operation_type=operation_type,
        status="queued",
    )
    db.add(run)
    db.flush()

    associations = [
        GenerationRunSubsectionVersion(
            generation_run_id=run.id,
            subsection_version_id=source.subsection_version_id,
            position=source.position,
        )
        for source in sources
    ]

    db.add_all(associations)
    db.flush()

    return run
