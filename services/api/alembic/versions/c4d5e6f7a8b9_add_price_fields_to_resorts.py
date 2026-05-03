"""add price and operational fields to resorts

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa

revision = 'c4d5e6f7a8b9'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('resorts', sa.Column('price_tier', sa.String(16), nullable=True))
    op.add_column('resorts', sa.Column('adult_day_pass_peak_eur', sa.Numeric(7, 2), nullable=True))
    op.add_column('resorts', sa.Column('child_day_pass_peak_eur', sa.Numeric(7, 2), nullable=True))
    op.add_column('resorts', sa.Column('adult_6day_pass_eur', sa.Numeric(7, 2), nullable=True))
    op.add_column('resorts', sa.Column('child_6day_pass_eur', sa.Numeric(7, 2), nullable=True))
    op.add_column('resorts', sa.Column('ski_rental_day_eur', sa.Numeric(7, 2), nullable=True))
    op.add_column('resorts', sa.Column('snowboard_rental_day_eur', sa.Numeric(7, 2), nullable=True))
    op.add_column('resorts', sa.Column('helmet_rental_day_eur', sa.Numeric(7, 2), nullable=True))
    op.add_column('resorts', sa.Column('opening_hours', sa.String(32), nullable=True))
    op.add_column('resorts', sa.Column('peak_months', sa.String(64), nullable=True))
    op.add_column('resorts', sa.Column('quiet_months', sa.String(64), nullable=True))
    op.add_column('resorts', sa.Column('ticket_url', sa.String(512), nullable=True))
    op.add_column('resorts', sa.Column('price_season', sa.String(16), nullable=True))
    op.add_column('resorts', sa.Column('venue_type', sa.String(16), nullable=True))


def downgrade() -> None:
    for col in ['price_tier','adult_day_pass_peak_eur','child_day_pass_peak_eur',
                'adult_6day_pass_eur','child_6day_pass_eur','ski_rental_day_eur',
                'snowboard_rental_day_eur','helmet_rental_day_eur','opening_hours',
                'peak_months','quiet_months','ticket_url','price_season','venue_type']:
        op.drop_column('resorts', col)