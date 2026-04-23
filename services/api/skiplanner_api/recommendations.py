"""
Rule-based resort recommendation engine.

Accepts user preferences and returns a ranked + filtered list of SkiArea
objects drawn from the database.  No ML required: rules are based on the
seed metadata already available on every SkiArea:

  - ``difficulty_hint`` matched against user ski_level
  - ``country`` matched against preferred_countries list
  - distance-to-airport tiebreaker (nearest_airport_iata presence)

The scoring is additive; every matching rule contributes a fixed number of
points so the caller can inspect ``score`` and understand *why* a resort
ranked where it did.

I/O Pydantic models (RecommendationRequest / RecommendationResponse /
ScoredResort) live in ``models.py`` so that all wire-format schemas stay in
one place and the router can import from a single module.
"""

from __future__ import annotations

from .models import RecommendationRequest, RecommendationResponse, ScoredResort, SkiArea

# ---------------------------------------------------------------------------
# Compatibility map: user level → acceptable difficulty_hint values
# ---------------------------------------------------------------------------

_LEVEL_COMPAT: dict[str, set[str]] = {
    "beginner": {"beginner", "mixed"},
    "intermediate": {"beginner", "intermediate", "mixed"},
    "advanced": {"intermediate", "advanced", "mixed"},
    "expert": {"advanced", "mixed", "expert"},
}

# Score weights
_SCORE_DIFFICULTY_MATCH = 30
_SCORE_DIFFICULTY_PERFECT = 10   # extra if user level == difficulty_hint
_SCORE_COUNTRY_MATCH = 20
_SCORE_HAS_AIRPORT = 5


# ---------------------------------------------------------------------------
# Core ranking function (pure — no DB access, easy to unit-test)
# ---------------------------------------------------------------------------

def rank_resorts(
    resorts: list[SkiArea],
    request: RecommendationRequest,
) -> RecommendationResponse:
    """
    Rank *resorts* according to *request* preferences.

    Parameters
    ----------
    resorts:
        Full list of available ``SkiArea`` objects (typically loaded from DB).
    request:
        User preferences.

    Returns
    -------
    RecommendationResponse
        Filtered and ranked list (length <= ``request.limit``).
    """
    total = len(resorts)
    scored: list[ScoredResort] = []

    # Normalise country filter once
    preferred = (
        {c.upper() for c in request.preferred_countries}
        if request.preferred_countries
        else set()
    )

    for resort in resorts:
        score = 0
        reasons: list[str] = []

        # ── Difficulty filter & scoring ──────────────────────────────────────
        if request.ski_level:
            allowed = _LEVEL_COMPAT.get(request.ski_level, set())
            hint = (resort.difficulty_hint or "").lower()

            if hint and hint not in allowed:
                # Incompatible — exclude entirely
                continue

            if hint and hint in allowed:
                score += _SCORE_DIFFICULTY_MATCH
                reasons.append(f"difficulty '{hint}' suits {request.ski_level} skiers")

                if hint == request.ski_level:
                    score += _SCORE_DIFFICULTY_PERFECT
                    reasons.append("difficulty is a perfect level match")

            # No hint → we don't exclude but we don't add points either

        # ── Country preference scoring ───────────────────────────────────────
        if preferred and resort.country and resort.country.upper() in preferred:
            score += _SCORE_COUNTRY_MATCH
            reasons.append(f"country '{resort.country}' matches preference")

        # ── Airport availability tiebreaker ─────────────────────────────────
        if resort.nearest_airport_iata:
            score += _SCORE_HAS_AIRPORT
            reasons.append(f"served by airport {resort.nearest_airport_iata}")

        scored.append(ScoredResort(resort=resort, score=score, match_reasons=reasons))

    # Sort descending by score, then alphabetically by name for stable output
    scored.sort(key=lambda s: (-s.score, s.resort.name))

    warning: str | None = None
    if not scored:
        warning = (
            "No resorts matched your preferences. "
            "Try broadening your ski level or removing country filters."
        )

    return RecommendationResponse(
        results=scored[: request.limit],
        total_evaluated=total,
        warning=warning,
    )
