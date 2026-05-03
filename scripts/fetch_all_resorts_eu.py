"""
Fetch all ski resorts in Europe from OpenStreetMap and write to data/seed/resorts.json.
Run from repo root:
    python scripts/fetch_all_resorts_eu.py
"""
import json
import math
import time
import urllib.request
import urllib.parse
from pathlib import Path

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "seed" / "resorts.json"

# Major airports near ski areas in Europe (lat, lon, iata)
AIRPORTS = [
    ("GVA", 46.2381,  6.1089),   # Geneva
    ("ZRH", 47.4582,  8.5555),   # Zurich
    ("INN", 47.2602, 11.3439),   # Innsbruck
    ("SZG", 47.7933, 13.0043),   # Salzburg
    ("CMF", 45.6380,  5.8803),   # Chambéry
    ("GNB", 45.3629,  5.3294),   # Grenoble
    ("BZO", 46.4602, 11.3264),   # Bolzano
    ("VCE", 45.5053, 12.3519),   # Venice
    ("BGY", 45.6740,  9.7042),   # Bergamo
    ("MXP", 45.6306,  8.7281),   # Milan Malpensa
    ("TRN", 45.2008,  7.6497),   # Turin
    ("VRN", 45.3957, 10.8885),   # Verona
    ("SIR", 46.2197,  7.3267),   # Sion
    ("BRN", 46.9141,  7.4970),   # Berne
    ("MUC", 48.3538, 11.7861),   # Munich
    ("NUE", 49.4987, 11.0669),   # Nuremberg
    ("OSL", 60.1939, 11.1004),   # Oslo
    ("OSD", 63.1944, 14.5003),   # Östersund/Åre
    ("TRF", 59.1867, 10.2586),   # Sandefjord
    ("BGO", 60.2934,  5.2181),   # Bergen
    ("SOF", 42.6952, 23.4063),   # Sofia
    ("KRK", 50.0777, 19.7848),   # Kraków
    ("BTS", 48.1702, 17.2127),   # Bratislava
    ("KSC", 48.6631, 21.2411),   # Košice
    ("BCN", 41.2971,  2.0785),   # Barcelona
    ("TLS", 43.6293,  1.3638),   # Toulouse
    ("GRX", 37.1887, -3.7774),   # Granada
    ("LJU", 46.2237, 14.4576),   # Ljubljana
    ("VIE", 48.1103, 16.5697),   # Vienna
    ("PRG", 50.1008, 14.2600),   # Prague
    ("OTP", 44.5711, 26.0850),   # Bucharest
    ("WAW", 52.1657, 20.9671),   # Warsaw
    ("BUD", 47.4369, 19.2556),   # Budapest
    ("OSR", 49.6963, 17.9052),   # Ostrava
]

# European countries to query: (country_code, OSM country name)
COUNTRIES = [
    ("FR", "France"),
    ("CH", "Switzerland"),
    ("AT", "Austria"),
    ("IT", "Italy"),
    ("DE", "Germany"),
    ("NO", "Norway"),
    ("SE", "Sweden"),
    ("ES", "Spain"),
    ("AD", "Andorra"),
    ("BG", "Bulgaria"),
    ("SK", "Slovakia"),
    ("PL", "Poland"),
    ("SI", "Slovenia"),
    ("CZ", "Czechia"),
    ("RO", "Romania"),
    ("LI", "Liechtenstein"),
]


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
    s = s.replace("ä", "a").replace("ö", "o").replace("ü", "u").replace("ß", "ss")
    s = s.replace("å", "a").replace("ø", "o").replace("æ", "ae")
    s = s.replace("é", "e").replace("è", "e").replace("ê", "e").replace("ë", "e")
    s = s.replace("à", "a").replace("â", "a").replace("á", "a").replace("ã", "a")
    s = s.replace("î", "i").replace("ï", "i").replace("í", "i").replace("ì", "i")
    s = s.replace("ô", "o").replace("ó", "o").replace("ò", "o").replace("õ", "o")
    s = s.replace("ù", "u").replace("û", "u").replace("ú", "u")
    s = s.replace("ç", "c").replace("ñ", "n").replace("ý", "y")
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = s.strip("_")
    return s


def fetch_country(country_code, country_name):
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

    # Get coordinates
    if el["type"] == "node":
        lat, lon = el["lat"], el["lon"]
    elif "center" in el:
        lat, lon = el["center"]["lat"], el["center"]["lon"]
    else:
        return None

    # Build bounds from bounding box if available
    bounds = None
    if "bounds" in el:
        b = el["bounds"]
        bounds = {
            "min_lat": round(b["minlat"], 5),
            "max_lat": round(b["maxlat"], 5),
            "min_lon": round(b["minlon"], 5),
            "max_lon": round(b["maxlon"], 5),
        }
        # Skip tiny areas (less than ~0.5km² — probably just a single run)
        lat_span = b["maxlat"] - b["minlat"]
        lon_span = b["maxlon"] - b["minlon"]
        if lat_span < 0.005 and lon_span < 0.005:
            return None

    return {
        "id": slugify(name),
        "name": name,
        "country": country_code,
        "centroid_lat": round(lat, 6),
        "centroid_lon": round(lon, 6),
        "bounds": bounds,
        "source": "osm",
        "source_version": "2026-05-03",
        "nearest_airport_iata": nearest_airport(lat, lon),
        "difficulty_hint": "mixed",
    }


def main():
    all_resorts = {}  # id -> resort (dedup by id)
    total_found = 0

    for country_code, country_name in COUNTRIES:
        print(f"  Fetching {country_name} ({country_code})...", end=" ", flush=True)
        try:
            data = fetch_country(country_code, country_name)
            elements = data.get("elements", [])
            count = 0
            for el in elements:
                resort = element_to_resort(el, country_code)
                if resort is None:
                    continue
                rid = resort["id"]
                if rid in all_resorts:
                    # Keep the one with bounds if possible
                    if resort["bounds"] and not all_resorts[rid]["bounds"]:
                        all_resorts[rid] = resort
                else:
                    all_resorts[rid] = resort
                    count += 1
            total_found += count
            print(f"{count} resorts found")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(2)  # Be polite to Overpass API

    resorts = sorted(all_resorts.values(), key=lambda r: (r["country"], r["name"]))

    OUTPUT_PATH.write_text(
        json.dumps(resorts, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nDone! {len(resorts)} resorts saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    print("Fetching all European ski resorts from OpenStreetMap...")
    main()