"""update_schema

Revision ID: 9f22b5e5a123
Revises: 005f66b4d4a8
Create Date: 2025-09-18 18:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '9f22b5e5a123'
down_revision: Union[str, None] = '005f66b4d4a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add any schema modifications here
    pass


def downgrade() -> None:
    # Add code to downgrade schema changes
    pass