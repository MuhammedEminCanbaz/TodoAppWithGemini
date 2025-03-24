"""phone number added

Revision ID: 82ba486e8900
Revises: 
Create Date: 2025-03-23 22:46:15.374617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82ba486e8900'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column("phone_number",sa.String(),nullable=True))


def downgrade() -> None:
    pass
