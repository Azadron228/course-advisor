"""add lessons table

Revision ID: 35088e8d2460
Revises: aa25908536e6
Create Date: 2026-05-04 14:53:40.840795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35088e8d2460'
down_revision: Union[str, Sequence[str], None] = 'aa25908536e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create lessons table
    op.create_table(
        'lessons',
        sa.Column('id', sa.Integer(), autoincrement=True, primary_key=True),
        sa.Column('plan_id', sa.Integer(), sa.ForeignKey('learning_plans.id', ondelete='CASCADE'), nullable=False),
        sa.Column('material_id', sa.Integer(), sa.ForeignKey('course_materials.id', ondelete='SET NULL'), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='upcoming'),
        sa.Column('is_external', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('external_url', sa.String(), nullable=True),
        sa.Column('additional_resources', sa.JSON(), nullable=False, server_default='[]'),
    )
    op.create_index(op.f('ix_lessons_order'), 'lessons', ['order'], unique=False)

    # Drop steps from learning_plans
    op.drop_column('learning_plans', 'steps')


def downgrade() -> None:
    # Re-add steps column to learning_plans
    op.add_column('learning_plans', sa.Column('steps', sa.JSON(), nullable=True))
    
    # Drop lessons table
    op.drop_index(op.f('ix_lessons_order'), table_name='lessons')
    op.drop_table('lessons')
