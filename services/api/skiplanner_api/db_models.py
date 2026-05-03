from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ResortRow(Base):
    __tablename__ = "resorts"

    id: Mapped[str] = mapped_column(String(128), primary_key=True)
    name: Mapped[str] = mapped_column(String(512), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    centroid_lat: Mapped[float] = mapped_column(Float, nullable=False)
    centroid_lon: Mapped[float] = mapped_column(Float, nullable=False)
    centroid_geom: Mapped[Optional[object]] = mapped_column(
        Geometry("POINT", srid=4326), nullable=True
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="seed")
    source_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nearest_airport_iata: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    difficulty_hint: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    venue_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)

    # Pricing fields (season 2025/26)
    price_tier: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    price_season: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    adult_day_pass_peak_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    child_day_pass_peak_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    adult_6day_pass_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    child_6day_pass_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    ski_rental_day_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    snowboard_rental_day_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)
    helmet_rental_day_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(7, 2), nullable=True)

    # Operational info
    opening_hours: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    peak_months: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    quiet_months: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    # Links
    ticket_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Trail(Base):
    __tablename__ = "trails"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)  # osm_type + osm_id e.g. "way/123"
    resort_id: Mapped[str] = mapped_column(String(64), ForeignKey("resorts.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    piste_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)   # downhill, nordic, skitour, etc.
    piste_difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # novice, easy, intermediate, advanced, expert, freeride
    grooming: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    oneway: Mapped[Optional[bool]] = mapped_column(nullable=True)
    geometry: Mapped[Optional[object]] = mapped_column(Geometry("LINESTRING", srid=4326), nullable=True)
    osm_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Lift(Base):
    __tablename__ = "lifts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    resort_id: Mapped[str] = mapped_column(String(64), ForeignKey("resorts.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    aerialway_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # cable_car, gondola, chair_lift, drag_lift, etc.
    capacity: Mapped[Optional[int]] = mapped_column(nullable=True)  # persons/hour
    geometry: Mapped[Optional[object]] = mapped_column(Geometry("LINESTRING", srid=4326), nullable=True)
    osm_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
