"""
Contract (smoke) tests for all SkiPlannerAI REST endpoints.

Uses FastAPI/Starlette TestClient with ASGI transport — no real server required.
Seeded resort IDs known from data/seed/resorts.json:
  - "chamonix"  (has a GeoJSON map file)
  - "verbier"   (has a GeoJSON map file)
  - "zermatt"   (has a GeoJSON map file)
"""
import pytest

# ---------------------------------------------------------------------------
# 1. GET /health
# ---------------------------------------------------------------------------

def test_health_ok(client):
    """Health endpoint returns 200 with status=ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("status") == "ok"


# ---------------------------------------------------------------------------
# 2. GET /resorts
# ---------------------------------------------------------------------------

def test_list_resorts_ok(client):
    """Resorts list returns 200 and a non-empty list with required fields."""
    resp = client.get("/resorts")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "id" in item, "missing 'id'"
        assert "name" in item, "missing 'name'"
        assert "country" in item, "missing 'country'"


# ---------------------------------------------------------------------------
# 3. GET /resorts/{id} — valid id
# ---------------------------------------------------------------------------

def test_get_resort_valid(client):
    """Known resort id returns 200 with correct shape."""
    resp = client.get("/resorts/chamonix")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "chamonix"
    assert "name" in body
    assert "country" in body
    assert "centroid_lat" in body
    assert "centroid_lon" in body


# ---------------------------------------------------------------------------
# 4. GET /resorts/{id} — nonexistent id
# ---------------------------------------------------------------------------

def test_get_resort_not_found(client):
    """Unknown resort id returns 404."""
    resp = client.get("/resorts/nonexistent")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 5. GET /resorts/{id}/map — valid id with GeoJSON file
# ---------------------------------------------------------------------------

def test_get_resort_map_valid(client):
    """Map endpoint for a seeded resort with a GeoJSON file returns 200 FeatureCollection."""
    resp = client.get("/resorts/chamonix/map")
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("type") == "FeatureCollection"
    assert "features" in body
    assert isinstance(body["features"], list)


# ---------------------------------------------------------------------------
# 6. GET /resorts/{id}/map — resort without a GeoJSON file
#    Accept either 404 OR a valid empty FeatureCollection (per spec)
# ---------------------------------------------------------------------------

def test_get_resort_map_no_geojson(client):
    """
    Map endpoint for a resort with no GeoJSON returns either:
      - 404, OR
      - 200 with type=FeatureCollection and empty features list.
    We use a resort id that exists in the seed but has no map file.
    If all seeded resorts have map files, we use a nonexistent resort (expect 404).
    """
    # "nonexistent_resort" doesn't exist in resorts → must 404
    resp = client.get("/resorts/nonexistent_resort/map")
    if resp.status_code == 404:
        return  # expected
    # In case the implementation returns a 200 empty collection instead
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("type") == "FeatureCollection"
    assert body.get("features") == []


# ---------------------------------------------------------------------------
# 7. POST /flights/search — valid body
# ---------------------------------------------------------------------------

def test_flight_search_valid(client):
    """Valid flight search returns 200 with offers list and deep_link_url."""
    payload = {
        "origin_iata": "ZRH",
        "destination_iata": "CDG",
        "departure_date": "2026-12-01",
    }
    resp = client.post("/flights/search", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert "offers" in body, "response missing 'offers'"
    assert isinstance(body["offers"], list)
    assert "deep_link_url" in body, "response missing 'deep_link_url'"
    assert body["deep_link_url"].startswith("https://"), "deep_link_url is not a valid URL"


# ---------------------------------------------------------------------------
# 8. POST /flights/search — missing required fields → 422
# ---------------------------------------------------------------------------

def test_flight_search_missing_fields(client):
    """Incomplete flight search body returns 422 Unprocessable Entity."""
    # Missing destination_iata and departure_date
    resp = client.post("/flights/search", json={"origin_iata": "ZRH"})
    assert resp.status_code == 422
