"""widen resort id and name columns

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa

revision = 'b3c4d5e6f7a8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('resorts', 'id',   existing_type=sa.VARCHAR(64),  type_=sa.VARCHAR(128))
    op.alter_column('resorts', 'name', existing_type=sa.VARCHAR(256), type_=sa.VARCHAR(512))


def downgrade() -> None:
    op.alter_column('resorts', 'id',   existing_type=sa.VARCHAR(128), type_=sa.VARCHAR(64))
    op.alter_column('resorts', 'name', existing_type=sa.VARCHAR(256), type_=sa.VARCHAR(256))