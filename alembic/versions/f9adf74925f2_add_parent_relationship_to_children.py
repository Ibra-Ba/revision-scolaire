
"""add parent relationship to children

Revision ID: f9adf74925f2
Revises: a1c8e5f2006a
Create Date: 2026-11-07 12:52:13.788629
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "f9adf74925f2"
down_revision: str | None = "a1c8e5f2006a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()

    # 1. Ajouter temporairement la colonne sans contrainte NOT NULL.
    op.add_column(
        "children",
        sa.Column("adult_user_id", sa.UUID(), nullable=True),
    )

    # 2. Récupérer les comptes parents existants.
    adult_ids = connection.execute(
        sa.text("SELECT id FROM adult_users")
    ).scalars().all()

    child_count = connection.execute(
        sa.text("SELECT COUNT(*) FROM children")
    ).scalar_one()

    # 3. Rattacher les enfants existants au parent unique.
    if child_count > 0:
        if len(adult_ids) != 1:
            raise RuntimeError(
                "Migration impossible : les enfants existants "
                "nécessitent exactement un compte parent."
            )

        connection.execute(
            sa.text(
                "UPDATE children "
                "SET adult_user_id = :adult_id"
            ),
            {"adult_id": adult_ids[0]},
        )

    # 4. Créer la clé étrangère avec un nom explicite.
    op.create_foreign_key(
        "fk_children_adult_user_id_adult_users",
        "children",
        "adult_users",
        ["adult_user_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 5. Créer l'index.
    op.create_index(
        "ix_children_adult_user_id",
        "children",
        ["adult_user_id"],
        unique=False,
    )

    # 6. Imposer la présence d'un parent pour chaque enfant.
    op.alter_column(
        "children",
        "adult_user_id",
        existing_type=sa.UUID(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_children_adult_user_id_adult_users",
        "children",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_children_adult_user_id",
        table_name="children",
    )

    op.drop_column("children", "adult_user_id")
