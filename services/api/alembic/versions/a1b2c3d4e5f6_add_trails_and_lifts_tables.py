"""add trails and lifts tables

Revision ID: a1b2c3d4e5f6
Revises: 86b7e43ee24e
Create Date: 2026-04-12 12:00:00.000000

"""
from typing import Sequence, Union

import geoalchemy2
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '86b7e43ee24e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('trails',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('resort_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('piste_type', sa.String(length=50), nullable=True),
    sa.Column('piste_difficulty', sa.String(length=50), nullable=True),
    sa.Column('grooming', sa.String(length=100), nullable=True),
    sa.Column('oneway', sa.Boolean(), nullable=True),
    sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.Column('osm_tags', sa.JSON(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['resort_id'], ['resorts.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trails_resort_id'), 'trails', ['resort_id'], unique=False)
    op.create_index('idx_trails_geometry', 'trails', ['geometry'], unique=False, postgresql_using='gist', if_not_exists=True)

    op.create_table('lifts',
    sa.Column('id', sa.String(length=64), nullable=False),
    sa.Column('resort_id', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('aerialway_type', sa.String(length=50), nullable=True),
    sa.Column('capacity', sa.Integer(), nullable=True),
    sa.Column('geometry', geoalchemy2.types.Geometry(geometry_type='LINESTRING', srid=4326, dimension=2, from_text='ST_GeomFromEWKT', name='geometry'), nullable=True),
    sa.Column('osm_tags', sa.JSON(), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['resort_id'], ['resorts.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lifts_resort_id'), 'lifts', ['resort_id'], unique=False)
    op.create_index('idx_lifts_geometry', 'lifts', ['geometry'], unique=False, postgresql_using='gist', if_not_exists=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_lifts_geometry', table_name='lifts', postgresql_using='gist')
    op.drop_index(op.f('ix_lifts_resort_id'), table_name='lifts')
    op.drop_table('lifts')
    op.drop_index('idx_trails_geometry', table_name='trails', postgresql_using='gist')
    op.drop_index(op.f('ix_trails_resort_id'), table_name='trails')
    op.drop_table('trails')
