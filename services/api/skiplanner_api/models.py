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


# ---------------------------------------------------------------------------
# Recommendation models
# ---------------------------------------------------------------------------

SkiLevel = Literal["beginner", "intermediate", "advanced", "expert"]


class RecommendationRequest(BaseModel):
    """Preferences submitted by the user (all fields optional)."""

    ski_level: SkiLevel | None = Field(
        None,
        description=(
            "User ski level. When set, resorts whose difficulty_hint is "
            "incompatible are excluded; compatible ones receive a score bonus."
        ),
    )
    preferred_countries: list[str] | None = Field(
        None,
        description=(
            "ISO 3166-1 alpha-2 country codes the user is interested in "
            "(e.g. ['CH', 'FR']).  When provided, matching resorts are "
            "boosted but non-matching ones are *not* excluded."
        ),
    )
    limit: int = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of resorts to return (default 10).",
    )


class ScoredResort(BaseModel):
    """A resort with its recommendation score and a human-readable reason."""

    resort: SkiArea
    score: int = Field(..., description="Higher is better.")
    match_reasons: list[str] = Field(default_factory=list)


class RecommendationResponse(BaseModel):
    """Ranked list of resorts and meta-information."""

    results: list[ScoredResort]
    total_evaluated: int
    warning: str | None = None
