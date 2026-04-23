"""add users table

Revision ID: e407ce43f4d8
Revises: initial
Create Date: 2026-04-14 11:24:44.097060

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e407ce43f4d8"
down_revision: Union[str, Sequence[str], None] = "initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(), unique=True, index=True, nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("disabled", sa.Boolean(), default=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
