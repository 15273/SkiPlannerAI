"""
Tests for the rule-based recommendation engine.

Covers:
  - Unit tests for ``rank_resorts`` (pure function, no DB)
  - HTTP contract tests for ``POST /recommendations`` via TestClient
"""
import pytest

from skiplanner_api.models import RecommendationRequest, SkiArea
from skiplanner_api.recommendations import rank_resorts

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

_RESORTS = [
    SkiArea(
        id="beginner_resort",
        name="Green Valley",
        country="FR",
        centroid_lat=45.0,
        centroid_lon=6.0,
        source="test",
        difficulty_hint="beginner",
        nearest_airport_iata="CDG",
    ),
    SkiArea(
        id="intermediate_resort",
        name="Blue Peak",
        country="CH",
        centroid_lat=46.0,
        centroid_lon=7.0,
        source="test",
        difficulty_hint="intermediate",
        nearest_airport_iata="GVA",
    ),
    SkiArea(
        id="advanced_resort",
        name="Black Diamond",
        country="AT",
        centroid_lat=47.0,
        centroid_lon=10.0,
        source="test",
        difficulty_hint="advanced",
        nearest_airport_iata="INN",
    ),
    SkiArea(
        id="mixed_resort",
        name="All Levels Mountain",
        country="FR",
        centroid_lat=45.5,
        centroid_lon=6.5,
        source="test",
        difficulty_hint="mixed",
        nearest_airport_iata="LYS",
    ),
    SkiArea(
        id="no_hint_resort",
        name="Mystery Mountain",
        country="IT",
        centroid_lat=46.5,
        centroid_lon=11.0,
        source="test",
        difficulty_hint=None,
        nearest_airport_iata=None,
    ),
]


# ---------------------------------------------------------------------------
# 1. Unit tests — rank_resorts (pure function)
# ---------------------------------------------------------------------------

class TestRankResortsNoPreferences:
    """With no preferences, all resorts are returned scored by airport tiebreaker."""

    def test_returns_all_resorts(self):
        req = RecommendationRequest()
        resp = rank_resorts(_RESORTS, req)
        assert resp.total_evaluated == len(_RESORTS)
        assert len(resp.results) == len(_RESORTS)

    def test_no_warning_when_results_present(self):
        req = RecommendationRequest()
        resp = rank_resorts(_RESORTS, req)
        assert resp.warning is None

    def test_airport_tiebreaker_boosts_score(self):
        """Resorts with a nearest_airport_iata should score higher than ones without."""
        req = RecommendationRequest()
        resp = rank_resorts(_RESORTS, req)
        # no_hint_resort has no airport — should be last or among lowest scored
        scored_ids = [s.resort.id for s in resp.results]
        no_hint_idx = scored_ids.index("no_hint_resort")
        # All other resorts have airports, so no_hint should come after them
        assert no_hint_idx == len(resp.results) - 1


class TestRankResortsBeginner:
    """Beginner level should exclude advanced resorts."""

    def test_excludes_advanced_difficulty(self):
        req = RecommendationRequest(ski_level="beginner")
        resp = rank_resorts(_RESORTS, req)
        ids = [s.resort.id for s in resp.results]
        assert "advanced_resort" not in ids

    def test_includes_beginner_and_mixed(self):
        req = RecommendationRequest(ski_level="beginner")
        resp = rank_resorts(_RESORTS, req)
        ids = [s.resort.id for s in resp.results]
        assert "beginner_resort" in ids
        assert "mixed_resort" in ids

    def test_intermediate_excluded_for_beginner(self):
        req = RecommendationRequest(ski_level="beginner")
        resp = rank_resorts(_RESORTS, req)
        ids = [s.resort.id for s in resp.results]
        assert "intermediate_resort" not in ids

    def test_perfect_match_scores_higher_than_mixed(self):
        req = RecommendationRequest(ski_level="beginner")
        resp = rank_resorts(_RESORTS, req)
        score_by_id = {s.resort.id: s.score for s in resp.results}
        # beginner_resort is a perfect match (difficulty == level) → extra bonus
        assert score_by_id["beginner_resort"] > score_by_id["mixed_resort"]

    def test_match_reasons_populated(self):
        req = RecommendationRequest(ski_level="beginner")
        resp = rank_resorts(_RESORTS, req)
        beginner_scored = next(s for s in resp.results if s.resort.id == "beginner_resort")
        assert len(beginner_scored.match_reasons) > 0
        assert any("beginner" in r for r in beginner_scored.match_reasons)


class TestRankResortsAdvanced:
    """Advanced level should exclude beginner-only resorts."""

    def test_excludes_beginner_difficulty(self):
        req = RecommendationRequest(ski_level="advanced")
        resp = rank_resorts(_RESORTS, req)
        ids = [s.resort.id for s in resp.results]
        assert "beginner_resort" not in ids

    def test_includes_advanced_and_mixed_and_intermediate(self):
        req = RecommendationRequest(ski_level="advanced")
        resp = rank_resorts(_RESORTS, req)
        ids = [s.resort.id for s in resp.results]
        assert "advanced_resort" in ids
        assert "mixed_resort" in ids
        assert "intermediate_resort" in ids


class TestRankResortsCountryFilter:
    """Country preference boosts matching resorts without excluding others."""

    def test_fr_resorts_score_higher(self):
        req = RecommendationRequest(preferred_countries=["FR"])
        resp = rank_resorts(_RESORTS, req)
        score_by_country: dict[str, list[int]] = {}
        for s in resp.results:
            score_by_country.setdefault(s.resort.country or "", []).append(s.score)
        fr_scores = score_by_country.get("FR", [])
        other_scores = [v for k, vals in score_by_country.items() if k != "FR" for v in vals]
        # FR resorts should have higher *average* score
        assert sum(fr_scores) / len(fr_scores) > sum(other_scores) / len(other_scores)

    def test_non_matching_countries_still_returned(self):
        """Country filter boosts but does NOT exclude non-matching resorts."""
        req = RecommendationRequest(preferred_countries=["FR"])
        resp = rank_resorts(_RESORTS, req)
        ids = [s.resort.id for s in resp.results]
        assert "advanced_resort" in ids  # AT resort, not FR

    def test_country_match_reason_present(self):
        req = RecommendationRequest(preferred_countries=["CH"])
        resp = rank_resorts(_RESORTS, req)
        ch_scored = next(s for s in resp.results if s.resort.country == "CH")
        assert any("CH" in r for r in ch_scored.match_reasons)

    def test_country_codes_are_case_insensitive(self):
        req_upper = RecommendationRequest(preferred_countries=["CH"])
        req_lower = RecommendationRequest(preferred_countries=["ch"])
        resp_upper = rank_resorts(_RESORTS, req_upper)
        resp_lower = rank_resorts(_RESORTS, req_lower)
        scores_upper = {s.resort.id: s.score for s in resp_upper.results}
        scores_lower = {s.resort.id: s.score for s in resp_lower.results}
        assert scores_upper == scores_lower


class TestRankResortsNoMatch:
    """When no resorts survive the difficulty filter, return empty with warning."""

    def test_expert_returns_empty_for_beginner_only_data(self):
        beginner_only = [
            SkiArea(
                id="b1",
                name="Bunny Slope",
                country="FR",
                centroid_lat=45.0,
                centroid_lon=6.0,
                source="test",
                difficulty_hint="beginner",
            )
        ]
        req = RecommendationRequest(ski_level="expert")
        resp = rank_resorts(beginner_only, req)
        assert resp.results == []
        assert resp.warning is not None
        assert "No resorts matched" in resp.warning

    def test_total_evaluated_reflects_input_size(self):
        req = RecommendationRequest(ski_level="expert")
        resp = rank_resorts(_RESORTS, req)
        assert resp.total_evaluated == len(_RESORTS)


class TestRankResortsLimit:
    """``limit`` caps the number of returned results."""

    def test_limit_one(self):
        req = RecommendationRequest(limit=1)
        resp = rank_resorts(_RESORTS, req)
        assert len(resp.results) == 1

    def test_limit_larger_than_pool(self):
        req = RecommendationRequest(limit=100)
        resp = rank_resorts(_RESORTS, req)
        assert len(resp.results) == len(_RESORTS)


# ---------------------------------------------------------------------------
# 2. HTTP contract tests — POST /recommendations
# ---------------------------------------------------------------------------

def test_recommendations_no_prefs(client):
    """POST /recommendations with empty body returns 200 and a list."""
    resp = client.post("/recommendations", json={})
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    assert isinstance(body["results"], list)
    assert len(body["results"]) > 0
    assert "total_evaluated" in body


def test_recommendations_beginner(client):
    """Beginner request excludes advanced resorts from seeded data."""
    resp = client.post("/recommendations", json={"ski_level": "beginner"})
    assert resp.status_code == 200
    body = resp.json()
    difficulty_hints = [r["resort"]["difficulty_hint"] for r in body["results"]]
    # No advanced-only hints should appear
    assert "advanced" not in difficulty_hints


def test_recommendations_advanced(client):
    """Advanced request excludes beginner-only resorts."""
    resp = client.post("/recommendations", json={"ski_level": "advanced"})
    assert resp.status_code == 200
    body = resp.json()
    difficulty_hints = [r["resort"]["difficulty_hint"] for r in body["results"]]
    assert "beginner" not in difficulty_hints


def test_recommendations_country_filter(client):
    """Country filter boosts matching resorts and returns a valid ranked list."""
    resp = client.post(
        "/recommendations",
        json={"preferred_countries": ["FR", "CH"]},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) > 0
    # First result should be from FR or CH
    top_country = body["results"][0]["resort"]["country"]
    assert top_country in ("FR", "CH")


def test_recommendations_limit(client):
    """limit parameter caps the response size."""
    resp = client.post("/recommendations", json={"limit": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["results"]) <= 3


def test_recommendations_scored_resort_shape(client):
    """Each result item has resort, score, and match_reasons."""
    resp = client.post("/recommendations", json={})
    assert resp.status_code == 200
    first = resp.json()["results"][0]
    assert "resort" in first
    assert "score" in first
    assert "match_reasons" in first
    assert isinstance(first["match_reasons"], list)
    # resort has required SkiArea fields
    resort = first["resort"]
    for field in ("id", "name", "country", "centroid_lat", "centroid_lon"):
        assert field in resort, f"missing field '{field}' in resort"


def test_recommendations_invalid_ski_level(client):
    """Invalid ski_level value returns 422 Unprocessable Entity."""
    resp = client.post("/recommendations", json={"ski_level": "pro"})
    assert resp.status_code == 422


def test_recommendations_invalid_limit(client):
    """limit=0 is below the minimum and returns 422."""
    resp = client.post("/recommendations", json={"limit": 0})
    assert resp.status_code == 422
