"""add answers to test scores

Revision ID: a7f8e9c1d2b3
Revises: fff1a80f1966
Create Date: 2026-05-14 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'a7f8e9c1d2b3'
down_revision: Union[str, Sequence[str], None] = 'fff1a80f1966'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('user_test_scores', sa.Column('answers', sa.JSON(), nullable=True))

def downgrade() -> None:
    op.drop_column('user_test_scores', 'answers')
