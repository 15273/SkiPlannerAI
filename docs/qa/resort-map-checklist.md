# QA checklist: resort list and map layers

Use before tagging a release candidate for the MVP map experience.

## Data

- [x] Every `id` in [data/seed/resorts.json](../../data/seed/resorts.json) uses lowercase `snake_case` and matches optional map file `data/seed/maps/{id}.geojson`.
- [x] Centroids fall inside the country declared in `country` (spot-check on OSM or maps).
- [x] `nearest_airport_iata` is a valid 3-letter code where present.
- [x] `source` and `source_version` are set for traceability.

## API

- [ ] `GET /resorts` returns 200 and non-empty array in dev seed.
- [ ] `GET /resorts/{id}` returns 404 for unknown ids.
- [ ] `GET /resorts/{id}/map` returns `FeatureCollection` shape with `features` array (may be empty).
- [ ] For resorts with a `.geojson` file, features render as lines (not points-only) for pistes/lifts demo.

## Mobile

- [ ] App loads resort list from configured `apiBaseUrl`.
- [ ] Tapping a row opens an external map at approximately the centroid (smoke test).
- [ ] On device, LAN IP base URL is used (not `localhost`).

## Copy / compliance

- [ ] UI states that trail data may be community-sourced / demo until OSM ingest is wired.
- [ ] OSM attribution planned wherever OSM-derived geometry ships.
