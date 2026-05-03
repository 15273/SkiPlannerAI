"""Fetch missing countries that failed due to rate limiting."""
import json
import math
import time
import urllib.request
import urllib.parse
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "seed" / "resorts.json"

AIRPORTS = [
    ("GVA", 46.2381,  6.1089), ("ZRH", 47.4582,  8.5555),
    ("INN", 47.2602, 11.3439), ("SZG", 47.7933, 13.0043),
    ("CMF", 45.6380,  5.8803), ("GNB", 45.3629,  5.3294),
    ("BZO", 46.4602, 11.3264), ("VCE", 45.5053, 12.3519),
    ("BGY", 45.6740,  9.7042), ("MXP", 45.6306,  8.7281),
    ("TRN", 45.2008,  7.6497), ("VRN", 45.3957, 10.8885),
    ("SIR", 46.2197,  7.3267), ("BRN", 46.9141,  7.4970),
    ("MUC", 48.3538, 11.7861), ("KSC", 48.6631, 21.2411),
    ("BTS", 48.1702, 17.2127), ("OTP", 44.5711, 26.0850),
    ("VIE", 48.1103, 16.5697),
]

MISSING = [("AT", "Austria"), ("IT", "Italy"), ("SK", "Slovakia"), ("RO", "Romania")]


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def nearest_airport(lat, lon):
    best_iata, best_dist = "ZRH", 9999
    for iata, alat, alon in AIRPORTS:
        d = haversine_km(lat, lon, alat, alon)
        if d < best_dist:
            best_dist = d
            best_iata = iata
    return best_iata


def slugify(name):
    import re
    s = name.lower()
    for a, b in [("ä","a"),("ö","o"),("ü","u"),("ß","ss"),("å","a"),("ø","o"),("æ","ae"),
                 ("é","e"),("è","e"),("ê","e"),("ë","e"),("à","a"),("â","a"),("á","a"),
                 ("î","i"),("ï","i"),("í","i"),("ô","o"),("ó","o"),("ù","u"),("û","u"),
                 ("ú","u"),("ç","c"),("ñ","n"),("ý","y"),("ã","a"),("ì","i"),("õ","o"),("ò","o")]:
        s = s.replace(a, b)
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def fetch_country(country_code):
    query = f"""
[out:json][timeout:60];
area["ISO3166-1"="{country_code}"]["admin_level"="2"]->.country;
(
  relation["site"="piste"]["name"](area.country);
  relation["landuse"="winter_sports"]["name"](area.country);
  way["landuse"="winter_sports"]["name"](area.country);
  node["tourism"="ski_resort"]["name"](area.country);
  relation["tourism"="ski_resort"]["name"](area.country);
);
out center;
"""
    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data)
    req.add_header("User-Agent", "SkiPlannerAI/1.0")
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read())


def element_to_resort(el, country_code):
    tags = el.get("tags", {})
    name = tags.get("name") or tags.get("name:en")
    if not name:
        return None
    if el["type"] == "node":
        lat, lon = el["lat"], el["lon"]
    elif "center" in el:
        lat, lon = el["center"]["lat"], el["center"]["lon"]
    else:
        return None
    bounds = None
    if "bounds" in el:
        b = el["bounds"]
        if (b["maxlat"] - b["minlat"]) < 0.005 and (b["maxlon"] - b["minlon"]) < 0.005:
            return None
        bounds = {"min_lat": round(b["minlat"],5), "max_lat": round(b["maxlat"],5),
                  "min_lon": round(b["minlon"],5), "max_lon": round(b["maxlon"],5)}
    return {
        "id": slugify(name), "name": name, "country": country_code,
        "centroid_lat": round(lat, 6), "centroid_lon": round(lon, 6),
        "bounds": bounds, "source": "osm", "source_version": "2026-05-03",
        "nearest_airport_iata": nearest_airport(lat, lon), "difficulty_hint": "mixed",
    }


def main():
    existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    existing_ids = {r["id"] for r in existing}
    new_resorts = []

    for country_code, country_name in MISSING:
        print(f"  Fetching {country_name}...", end=" ", flush=True)
        time.sleep(10)  # Wait longer between requests
        try:
            data = fetch_country(country_code)
            count = 0
            for el in data.get("elements", []):
                resort = element_to_resort(el, country_code)
                if resort and resort["id"] not in existing_ids:
                    new_resorts.append(resort)
                    existing_ids.add(resort["id"])
                    count += 1
            print(f"{count} resorts found")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(5)

    all_resorts = sorted(existing + new_resorts, key=lambda r: (r["country"], r["name"]))
    OUTPUT_PATH.write_text(json.dumps(all_resorts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nDone! Total: {len(all_resorts)} resorts")


if __name__ == "__main__":
    print("Fetching missing countries...")
    main()
