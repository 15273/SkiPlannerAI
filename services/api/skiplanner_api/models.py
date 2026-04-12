from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class SkiArea(BaseModel):
    id: str
    name: str
    country: str
    centroid_lat: float = Field(..., ge=-90, le=90)
    centroid_lon: float = Field(..., ge=-180, le=180)
    bounds: dict[str, float] | None = None
    source: str
    source_version: str | None = None
    updated_at: datetime | None = None
    nearest_airport_iata: str | None = None
    difficulty_hint: Literal["beginner", "intermediate", "advanced", "mixed"] | None = None


class GeoJSONFeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[dict[str, Any]]
    metadata: dict[str, Any] | None = None


class FlightSearchRequest(BaseModel):
    origin_iata: str = Field(..., min_length=3, max_length=3)
    destination_iata: str = Field(..., min_length=3, max_length=3)
    departure_date: str = Field(..., description="ISO date YYYY-MM-DD")
    adults: int = Field(1, ge=1, le=9)
    max_stops: int | None = Field(None, ge=0, le=3)
    budget_eur: float | None = Field(None, gt=0)
    prefer: Literal["cheapest", "fastest", "balanced"] = "balanced"


class RankedFlightOffer(BaseModel):
    id: str
    price_total_eur: float | None = None
    duration_minutes: int | None = None
    num_stops: int | None = None
    carrier_summary: str | None = None
    raw: dict[str, Any] | None = None
    rank_reason: str


class FlightSearchResponse(BaseModel):
    offers: list[RankedFlightOffer]
    deep_link_url: str
    provider: Literal["amadeus", "none"]
    warning: str | None = None
