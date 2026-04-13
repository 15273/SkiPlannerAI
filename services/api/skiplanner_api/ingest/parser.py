"""Parse raw Overpass JSON into Trail and Lift pydantic-like dicts."""
from typing import Any
import uuid

PISTE_DIFFICULTY_MAP = {
    "novice": "novice",
    "easy": "easy",
    "intermediate": "intermediate",
    "advanced": "advanced",
    "expert": "expert",
    "freeride": "freeride",
}

AERIALWAY_TYPES = {
    "cable_car", "gondola", "chair_lift", "drag_lift",
    "t-bar", "j-bar", "platter", "rope_tow", "magic_carpet", "zip_line",
}


def _node_coords(nodes: list[int], node_map: dict[int, tuple[float, float]]) -> list[tuple[float, float]]:
    return [node_map[n] for n in nodes if n in node_map]


def parse_overpass(raw: dict[str, Any], resort_id: str) -> tuple[list[dict], list[dict]]:
    """Return (trails, lifts) as lists of dicts ready for ORM insertion."""
    elements = raw.get("elements", [])

    # Build node coordinate lookup
    node_map: dict[int, tuple[float, float]] = {}
    for el in elements:
        if el["type"] == "node":
            node_map[el["id"]] = (el["lon"], el["lat"])

    trails: list[dict] = []
    lifts: list[dict] = []

    for el in elements:
        if el["type"] != "way":
            continue
        tags = el.get("tags", {})
        node_ids = el.get("nodes", [])
        coords = _node_coords(node_ids, node_map)
        if len(coords) < 2:
            continue

        osm_id = f"way/{el['id']}"

        # Trail
        if "piste:type" in tags:
            trails.append({
                "id": osm_id,
                "resort_id": resort_id,
                "name": tags.get("name") or tags.get("piste:name"),
                "piste_type": tags.get("piste:type"),
                "piste_difficulty": PISTE_DIFFICULTY_MAP.get(tags.get("piste:difficulty", ""), None),
                "grooming": tags.get("piste:grooming"),
                "oneway": tags.get("piste:oneway") == "yes" if "piste:oneway" in tags else None,
                "coords": coords,
                "osm_tags": tags,
            })

        # Lift
        elif tags.get("aerialway") in AERIALWAY_TYPES:
            cap_str = tags.get("aerialway:capacity", "")
            capacity = int(cap_str) if cap_str.isdigit() else None
            lifts.append({
                "id": osm_id,
                "resort_id": resort_id,
                "name": tags.get("name"),
                "aerialway_type": tags.get("aerialway"),
                "capacity": capacity,
                "coords": coords,
                "osm_tags": tags,
            })

    return trails, lifts
