# OSM ingest specification (resorts, pistes, lifts)

## Goal

Produce normalized **GeoJSON** `FeatureCollection` files under [data/seed/maps](../../data/seed/maps) (or a future object store) from **OpenStreetMap**, with provenance on every feature.

## OSM tags (starting set)

| Feature | Typical tags |
|--------|----------------|
| Piste | `piste:type=downhill`, `piste:difficulty=*`, optional `name=*` |
| Lift | `aerialway=*` (chairlift, gondola, drag_lift, …) |
| Resort boundary / site | `site=ski_resort`, `landuse=winter_sports`, or named relations |

Coordinates must remain **WGS84** (lon, lat order in GeoJSON).

## Query strategy

### A) Overpass API (good for MVP scripts)

1. Resolve resort **centroid** from curated seed ([data/seed/resorts.json](../../data/seed/resorts.json)) or from an OSM relation id (future).
2. Build a **bounding box** (e.g. centroid ± 0.06° with clamping) or use a small `around:radius` query in meters.
3. Run Overpass with `out geom;` so ways include geometry.

Example pattern (illustrative — tune bbox per resort):

```text
[out:json][timeout:60];
(
  way["piste:type"]({{bbox}});
  way["aerialway"]({{bbox}});
);
out geom;
```

### B) Regional extract + local filter (stable for CI)

1. Download a **Geofabrik** extract for the launch region (e.g. Switzerland, France Rhône-Alpes).
2. Filter with **osmium** or **pyosmium** for keys `piste:type` and `aerialway` inside resort bounding polygons.

Prefer this when Overpass rate limits or reliability become an issue.

## Normalization pipeline

1. **Parse** OSM elements into line geometries (join way nodes).
2. **Classify** as `piste` vs `lift` from tags.
3. **Map difficulty** from `piste:difficulty` to app enums (`green|blue|red|black|unknown`).
4. **Emit** one `FeatureCollection` per resort id with `metadata.source=osm` and `metadata.generated_at=ISO8601`.
5. **Validate** with `geojsonhint` or equivalent; reject empty or invalid rings.

## Launch region

Initial curated seeds target the **Alps** (see `resorts.json`). Ingest jobs should start with resorts that have reliable OSM coverage (e.g. Chamonix, Verbier, Zermatt) before expanding.

## Legal / UX

OSM is **ODbL**. Preserve attribution in the app (“© OpenStreetMap contributors”) and store `source_version` (e.g. planet date or Overpass query time) on `SkiArea` and map metadata.
