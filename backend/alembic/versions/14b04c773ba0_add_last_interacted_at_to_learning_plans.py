"""add last_interacted_at to learning_plans

Revision ID: 14b04c773ba0
Revises: 35088e8d2460
Create Date: 2026-05-04 16:29:47.765085

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14b04c773ba0'
down_revision: Union[str, Sequence[str], None] = '35088e8d2460'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('learning_plans', sa.Column('last_interacted_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('learning_plans', 'last_interacted_at')
