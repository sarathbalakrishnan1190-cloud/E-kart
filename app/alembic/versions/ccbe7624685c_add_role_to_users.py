
"""add role to users

Revision ID: ccbe7624685c
Revises: 4f6370933452
Create Date: 2026-08-30 18:03:55.882382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ccbe7624685c'
down_revision: Union[str, Sequence[str], None] = '4f6370933452'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column(
            'role',
            sa.String(length=20),
            nullable=False,
            server_default='customer'
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')

