"""initial migration

Revision ID: initial
Revises: 
Create Date: 2026-04-09

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        'courses',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('subject_name', sa.String(), nullable=False),
        sa.Column('credits', sa.Float(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('skills_taught', sa.JSON(), nullable=False),
        sa.Column('difficulty', sa.Float(), sa.CheckConstraint('difficulty >= 0 AND difficulty <= 1')),
        sa.Column('workload', sa.Float(), sa.CheckConstraint('workload >= 0 AND workload <= 1')),
        sa.Column('embedding', Vector(1536))
    )

def downgrade():
    op.drop_table('courses')
    op.execute("DROP EXTENSION IF EXISTS vector")
