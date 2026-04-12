# Map API contract (MVP)

Base URL: same host as API (e.g. `http://localhost:8000`). OpenAPI UI: `/docs`.

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

## Shared OpenAPI

A static snapshot lives at [packages/shared/openapi/openapi.yaml](../../packages/shared/openapi/openapi.yaml). Regenerate when routes change (or rely on live `/openapi.json`).
