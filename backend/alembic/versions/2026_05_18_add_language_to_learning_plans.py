"""add language to learning_plans

Revision ID: b8e9f0a1b2c3
Revises: a7f8e9c1d2b3
Create Date: 2026-05-18 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b8e9f0a1b2c3'
down_revision: Union[str, Sequence[str], None] = 'a7f8e9c1d2b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.add_column('learning_plans', sa.Column('language', sa.String(), nullable=False, server_default='en'))

def downgrade() -> None:
    op.drop_column('learning_plans', 'language')
