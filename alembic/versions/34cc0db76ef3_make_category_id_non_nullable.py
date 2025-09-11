"""make category_id non-nullable

Revision ID: 34cc0db76ef3
Revises: de43b567c0ed
Create Date: 2025-09-11 18:03:52.355632

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34cc0db76ef3'
down_revision: Union[str, Sequence[str], None] = 'de43b567c0ed'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ensure "Uncategorized" category exists (safety net)
    op.execute("""
            INSERT INTO categories (name, owner_id, created_at, updated_at)
            VALUES ('Uncategorized', NULL, NOW(), NOW())
            ON CONFLICT (name) DO NOTHING;
        """)

    # Replace NULLs with Uncategorized just in case
    op.execute("""
            UPDATE expenses
            SET category_id = (
                SELECT id FROM categories WHERE name = 'Uncategorized' LIMIT 1
            )
            WHERE category_id IS NULL;
        """)

    # Finally make column non-nullable
    op.alter_column(
        'expenses',
        'category_id',
        existing_type=sa.Integer(),
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Allow category_id to be nullable again
    op.alter_column(
        'expenses',
        'category_id',
        existing_type=sa.Integer(),
        nullable=True
    )
