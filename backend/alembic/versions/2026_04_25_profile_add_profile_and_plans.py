"""add profile and plans

Revision ID: 2026_04_25_profile
Revises: e407ce43f4d8
Create Date: 2026-04-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2026_04_25_profile"
down_revision: Union[str, Sequence[str], None] = "e407ce43f4d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update users table
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=True))
    op.execute("UPDATE users SET is_admin = FALSE")
    op.alter_column("users", "is_admin", nullable=False, server_default="FALSE")
    
    op.add_column("users", sa.Column("career_goal", sa.String(), nullable=True))
    op.add_column("users", sa.Column("onboarding_completed", sa.Boolean(), server_default="FALSE", nullable=False))

    # Create user_skills table
    op.create_table(
        "user_skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("skill_name", sa.String(), nullable=False),
        sa.Column("mastery_level", sa.Integer(), server_default="0", nullable=False),
        sa.Column("category", sa.String(), nullable=False),
    )

    # Create user_transcripts table
    op.create_table(
        "user_transcripts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("subject_name", sa.String(), nullable=False),
        sa.Column("credits", sa.Float(), nullable=False),
        sa.Column("mark", sa.Float(), nullable=False),
    )

    # Create learning_plans table
    op.create_table(
        "learning_plans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("goal", sa.String(), nullable=False),
        sa.Column("steps", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="TRUE", nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("learning_plans")
    op.drop_table("user_transcripts")
    op.drop_table("user_skills")
    op.drop_column("users", "onboarding_completed")
    op.drop_column("users", "career_goal")
    op.drop_column("users", "is_admin")
