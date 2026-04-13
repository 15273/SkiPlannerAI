"""Fetch piste and aerialway features from the Overpass API for a given bounding box."""
import httpx
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
TIMEOUT = httpx.Timeout(60.0)  # Overpass can be slow

OVERPASS_QUERY = """
[out:json][timeout:55];
(
  way["piste:type"]({south},{west},{north},{east});
  relation["piste:type"]({south},{west},{north},{east});
  way["aerialway"]({south},{west},{north},{east});
  relation["aerialway"]({south},{west},{north},{east});
);
out body;
>;
out skel qt;
"""


def build_query(bounds: dict[str, float]) -> str:
    return OVERPASS_QUERY.format(
        south=bounds["south"],
        west=bounds["west"],
        north=bounds["north"],
        east=bounds["east"],
    )


async def fetch_overpass(bounds: dict[str, float]) -> dict[str, Any]:
    query = build_query(bounds)
    logger.info("Fetching Overpass data for bounds %s", bounds)
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(OVERPASS_URL, data={"data": query})
        resp.raise_for_status()
    result = resp.json()
    logger.info("Overpass returned %d elements", len(result.get("elements", [])))
    return result
