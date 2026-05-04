"""refactor schema for lesson isolation

Revision ID: 3046ccaa520b
Revises: 14b04c773ba0
Create Date: 2026-05-04 17:07:02.717006

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3046ccaa520b'
down_revision: Union[str, Sequence[str], None] = '14b04c773ba0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add content to lessons
    op.add_column('lessons', sa.Column('content', sa.Text(), nullable=True))

    # 2. Refactor practice_tests
    with op.batch_alter_table('practice_tests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lesson_id', sa.Integer(), nullable=True))
    
    # Associate existing practice tests with lessons if material_id matches
    # This is a best-effort migration
    op.execute("UPDATE practice_tests SET lesson_id = (SELECT id FROM lessons WHERE lessons.material_id = practice_tests.material_id LIMIT 1)")
    
    # Delete practice tests that couldn't be associated with a lesson
    op.execute("DELETE FROM practice_tests WHERE lesson_id IS NULL")

    with op.batch_alter_table('practice_tests', schema=None) as batch_op:
        batch_op.drop_column('material_id')
        batch_op.alter_column('lesson_id', nullable=False)
        batch_op.create_foreign_key('fk_practice_tests_lessons', 'lessons', ['lesson_id'], ['id'], ondelete='CASCADE')

    # 3. Refactor user_test_scores
    with op.batch_alter_table('user_test_scores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lesson_id', sa.Integer(), nullable=True))
    
    # Associate existing scores with lessons if material_id matches
    op.execute("UPDATE user_test_scores SET lesson_id = (SELECT id FROM lessons WHERE lessons.material_id = user_test_scores.material_id LIMIT 1)")
    
    # Delete scores that couldn't be associated with a lesson
    op.execute("DELETE FROM user_test_scores WHERE lesson_id IS NULL")

    with op.batch_alter_table('user_test_scores', schema=None) as batch_op:
        batch_op.drop_column('material_id')
        batch_op.alter_column('lesson_id', nullable=False)
        batch_op.create_foreign_key('fk_user_test_scores_lessons', 'lessons', ['lesson_id'], ['id'])


def downgrade() -> None:
    # 3. Revert user_test_scores
    with op.batch_alter_table('user_test_scores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('material_id', sa.Integer(), nullable=True))
    
    op.execute("UPDATE user_test_scores SET material_id = (SELECT material_id FROM lessons WHERE lessons.id = user_test_scores.lesson_id LIMIT 1)")

    with op.batch_alter_table('user_test_scores', schema=None) as batch_op:
        batch_op.drop_column('lesson_id')
        batch_op.alter_column('material_id', nullable=False)
        batch_op.create_foreign_key('user_test_scores_material_id_fkey', 'course_materials', ['material_id'], ['id'])

    # 2. Revert practice_tests
    with op.batch_alter_table('practice_tests', schema=None) as batch_op:
        batch_op.add_column(sa.Column('material_id', sa.Integer(), nullable=True))
    
    op.execute("UPDATE practice_tests SET material_id = (SELECT material_id FROM lessons WHERE lessons.id = practice_tests.lesson_id LIMIT 1)")

    with op.batch_alter_table('practice_tests', schema=None) as batch_op:
        batch_op.drop_column('lesson_id')
        batch_op.alter_column('material_id', nullable=False)
        batch_op.create_foreign_key('practice_tests_material_id_fkey', 'course_materials', ['material_id'], ['id'], ondelete='CASCADE')

    # 1. Remove content from lessons
    op.drop_column('lessons', 'content')
