"""remove_course_params_and_refactor_id

Revision ID: ca535974d892
Revises: f40bdbd2c133
Create Date: 2026-05-01 13:17:05.765925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca535974d892'
down_revision: Union[str, Sequence[str], None] = 'f40bdbd2c133'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Drop constraints first
    op.execute("ALTER TABLE courses DROP CONSTRAINT IF EXISTS courses_difficulty_check")
    op.execute("ALTER TABLE courses DROP CONSTRAINT IF EXISTS courses_workload_check")
    
    # 2. Drop columns
    op.drop_column('courses', 'difficulty')
    op.drop_column('courses', 'workload')
    op.drop_column('courses', 'credits')
    
    # 3. Refactor ID
    # Drop primary key constraint
    op.execute("ALTER TABLE courses DROP CONSTRAINT courses_pkey CASCADE")
    # Drop the string ID column
    op.drop_column('courses', 'id')
    # Add the new integer ID column
    op.add_column('courses', sa.Column('id', sa.Integer(), autoincrement=True, nullable=False))
    # Add primary key constraint
    op.create_primary_key("courses_pkey", "courses", ["id"])


def downgrade() -> None:
    # Drop integer ID
    op.execute("ALTER TABLE courses DROP CONSTRAINT courses_pkey CASCADE")
    op.drop_column('courses', 'id')
    # Add back string ID
    op.add_column('courses', sa.Column('id', sa.String(), primary_key=True))
    # Add back columns
    op.add_column('courses', sa.Column('credits', sa.Float(), nullable=False))
    op.add_column('courses', sa.Column('workload', sa.Float(), nullable=False))
    op.add_column('courses', sa.Column('difficulty', sa.Float(), nullable=False))
    # Add back constraints
    op.create_check_constraint("courses_difficulty_check", "courses", "difficulty >= 0 AND difficulty <= 1")
    op.create_check_constraint("courses_workload_check", "courses", "workload >= 0 AND workload <= 1")
