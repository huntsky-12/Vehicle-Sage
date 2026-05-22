"""add role column"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '98844573a2f9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'UserDetails',
        sa.Column(
            'role',
            sa.String(),
            nullable=False,
            server_default='user'
        )
    )


def downgrade() -> None:
    op.drop_column('UserDetails', 'role')