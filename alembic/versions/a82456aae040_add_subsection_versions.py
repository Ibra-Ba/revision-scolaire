
import hashlib
from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa

from alembic import op

revision: str = "a82456aae040"
down_revision: str | None = "b0a6c25bc9c0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subsection_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("subsection_id", sa.UUID(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("source_text", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("validated_by", sa.UUID(), nullable=True),
        sa.Column("validator_type", sa.String(length=10), nullable=True),
        sa.Column("validated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "version_number > 0",
            name="ck_subsection_version_number_positive",
        ),
        sa.ForeignKeyConstraint(
            ["subsection_id"],
            ["subsections.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "subsection_id",
            "version_number",
            name="uq_subsection_version_number",
        ),
    )

    op.create_index(
        op.f("ix_subsection_versions_subsection_id"),
        "subsection_versions",
        ["subsection_id"],
        unique=False,
    )

    # Reprise des contenus déjà validés
    bind = op.get_bind()

    subsections = bind.execute(
        sa.text("""
            SELECT
                id,
                source_text,
                validated_by,
                validator_type,
                validated_at
            FROM subsections
            WHERE status IN ('approved', 'published')
              AND source_text IS NOT NULL
              AND BTRIM(source_text) <> ''
              AND validated_at IS NOT NULL
        """)
    ).mappings().all()

    version_table = sa.table(
        "subsection_versions",
        sa.column("id", sa.UUID()),
        sa.column("subsection_id", sa.UUID()),
        sa.column("version_number", sa.Integer()),
        sa.column("source_text", sa.Text()),
        sa.column("content_hash", sa.String(64)),
        sa.column("validated_by", sa.UUID()),
        sa.column("validator_type", sa.String(10)),
        sa.column("validated_at", sa.DateTime(timezone=True)),
    )

    versions = []

    for subsection in subsections:
        source_text = subsection["source_text"]

        content_hash = hashlib.sha256(
            source_text.encode("utf-8")
        ).hexdigest()

        versions.append({
            "id": uuid4(),
            "subsection_id": subsection["id"],
            "version_number": 1,
            "source_text": source_text,
            "content_hash": content_hash,
            "validated_by": subsection["validated_by"],
            "validator_type": subsection["validator_type"],
            "validated_at": subsection["validated_at"],
        })

    if versions:
        bind.execute(version_table.insert(), versions)


def downgrade() -> None:
    op.drop_index(
        op.f("ix_subsection_versions_subsection_id"),
        table_name="subsection_versions",
    )
    op.drop_table("subsection_versions")
