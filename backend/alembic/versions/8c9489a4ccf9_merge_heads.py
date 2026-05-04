"""merge heads

Revision ID: 8c9489a4ccf9
Revises: 3046ccaa520b, 76220e01023f
Create Date: 2026-05-04 17:25:22.341936

"""
from typing import Sequence, Union



# revision identifiers, used by Alembic.
revision: str = '8c9489a4ccf9'
down_revision: Union[str, Sequence[str], None] = ('3046ccaa520b', '76220e01023f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
