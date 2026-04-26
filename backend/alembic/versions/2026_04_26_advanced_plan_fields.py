"""add advanced plan fields

Revision ID: 2026_04_26_advanced_plan
Revises: 2026_04_25_profile
Create Date: 2026-04-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_26_advanced_plan"
down_revision: Union[str, Sequence[str], None] = "2026_04_25_profile"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update users table
    op.add_column("users", sa.Column("default_skill_level", sa.String(), nullable=True))
    op.add_column("users", sa.Column("default_learning_style", sa.String(), nullable=True))
    op.add_column("users", sa.Column("default_study_time", sa.Integer(), server_default="10", nullable=True))
    op.add_column("users", sa.Column("interests", sa.JSON(), nullable=True))

    # Update learning_plans table
    op.add_column("learning_plans", sa.Column("skill_level", sa.String(), server_default="Beginner", nullable=False))
    op.add_column("learning_plans", sa.Column("learning_style", sa.String(), server_default="Practical", nullable=False))
    op.add_column("learning_plans", sa.Column("study_time", sa.Integer(), server_default="10", nullable=False))
    op.add_column("learning_plans", sa.Column("interests", sa.JSON(), server_default="[]", nullable=False))


def downgrade() -> None:
    op.drop_column("learning_plans", "interests")
    op.drop_column("learning_plans", "study_time")
    op.drop_column("learning_plans", "learning_style")
    op.drop_column("learning_plans", "skill_level")
    
    op.drop_column("users", "interests")
    op.drop_column("users", "default_study_time")
    op.drop_column("users", "default_learning_style")
    op.drop_column("users", "default_skill_level")
