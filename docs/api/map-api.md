# Map API contract (MVP)

Base URL: same host as API (e.g. `http://localhost:8040`). OpenAPI UI: `/docs`.

## Endpoints

### `GET /resorts`

Returns a JSON array of `SkiArea` objects (summary list).

**SkiArea fields**

| Field | Type | Notes |
|-------|------|--------|
| `id` | string | Stable slug, matches map filename |
| `name` | string | Display name |
| `country` | string | ISO 3166-1 alpha-2 |
| `centroid_lat` | number | WGS84 |
| `centroid_lon` | number | WGS84 |
| `bounds` | object? | Optional `min_lat`, `max_lat`, `min_lon`, `max_lon` |
| `source` | string | e.g. `curated_seed` |
| `source_version` | string? | Dataset version |
| `updated_at` | string (ISO 8601) | Set at load time if omitted in seed |
| `nearest_airport_iata` | string? | For flight deep links |
| `difficulty_hint` | string? | `beginner` / `intermediate` / `advanced` / `mixed` |

### `GET /resorts/{resort_id}`

Single `SkiArea`. `404` if unknown id.

### `GET /resorts/{resort_id}/map`

Returns a **GeoJSON-like** JSON object:

```json
{
  "type": "FeatureCollection",
  "features": [ /* GeoJSON features */ ],
  "metadata": {
    "resort_id": "chamonix",
    "source": "illustrative_demo | osm | …"
  }
}
```

- `features` follow standard GeoJSON semantics (`LineString` for pistes/lifts in MVP).
- If no file exists at `data/seed/maps/{resort_id}.geojson`, the API returns an empty `features` array and a metadata note (see implementation).

### `POST /recommendations`

Returns a ranked list of ski resorts based on user preferences.  All fields
are optional; an empty body returns all resorts ordered by airport-tiebreaker
score.

**Request body** (`application/json`)

| Field | Type | Notes |
|-------|------|--------|
| `ski_level` | string? | `"beginner"` / `"intermediate"` / `"advanced"` / `"expert"` |
| `preferred_countries` | string[]? | ISO 3166-1 alpha-2 codes, e.g. `["CH", "FR"]` |
| `limit` | integer? | Max results to return (1–100, default `10`) |

**Response** (`200 OK`)

```json
{
  "results": [
    {
      "resort": { /* SkiArea object */ },
      "score": 65,
      "match_reasons": [
        "difficulty 'advanced' suits advanced skiers",
        "difficulty is a perfect level match",
        "country 'CH' matches preference",
        "served by airport GVA"
      ]
    }
  ],
  "total_evaluated": 18,
  "warning": null
}
```

**Scoring rules (additive)**

| Rule | Points |
|------|--------|
| `difficulty_hint` compatible with `ski_level` | +30 |
| `difficulty_hint` is a perfect match (hint == level) | +10 extra |
| `country` in `preferred_countries` | +20 |
| `nearest_airport_iata` present | +5 |

Resorts whose `difficulty_hint` is *incompatible* with the requested
`ski_level` are **excluded** from results.  Country preference boosts score
but never excludes resorts.

**Error responses**

| Status | Condition |
|--------|-----------|
| `422` | Invalid `ski_level` value or `limit` out of range |

**Example**

```bash
curl -X POST http://localhost:8040/recommendations \
  -H "Content-Type: application/json" \
  -d '{"ski_level": "advanced", "preferred_countries": ["CH"], "limit": 5}'
```

## Shared OpenAPI

A static snapshot lives at [packages/shared/openapi/openapi.yaml](../../packages/shared/openapi/openapi.yaml). Regenerate when routes change (or rely on live `/openapi.json`).
