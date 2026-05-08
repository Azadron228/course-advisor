"""add cascade delete to user_test_scores

Revision ID: bd064950022f
Revises: ce4b669706d8
Create Date: 2026-05-06 13:51:11.644567

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'bd064950022f'
down_revision: Union[str, Sequence[str], None] = 'ce4b669706d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('user_test_scores', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_test_scores_lessons', type_='foreignkey')
        batch_op.create_foreign_key('fk_user_test_scores_lessons', 'lessons', ['lesson_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('user_test_scores', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_test_scores_lessons', type_='foreignkey')
        batch_op.create_foreign_key('fk_user_test_scores_lessons', 'lessons', ['lesson_id'], ['id'])
