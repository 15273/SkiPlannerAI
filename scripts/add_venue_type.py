"""
Add venue_type field to all resorts.
- "resort"   = full destination (hotels, village, major lifts) — curated entries
- "ski_area" = ski area only (may be small local hill) — OSM entries

Later, manual review via resorts_review.csv can refine these.
"""
import json
from pathlib import Path

PATH = Path(__file__).parent.parent / "data" / "seed" / "resorts.json"

# Known large resorts from OSM that should be "resort" not "ski_area"
KNOWN_RESORTS = {
    "grandvalira", "pal_arinsal", "bansko", "jasna", "zakopane",
    "are", "trysil", "hemsedal", "sierra_nevada", "baqueira_beret",
    "borovets", "poiana_brasov", "kranjska_gora", "mariborsko_pohorje",
    "schladming", "nassfeld", "bad_kleinkirchheim", "hochzillertal",
    "stubaier_gletscher", "zillertal_arena", "skiwelt_wilder_kaiser",
    "skirama_dolomiti", "passo_tonale", "sestriere", "monterosa_ski",
    "les_portes_du_soleil", "espace_killy", "les_contamines",
    "megeve", "la_clusaz", "le_grand_bornand", "les_menuires",
    "saint_gervais", "morzine", "avoriaz", "flaine", "samoens",
    "engelberg", "andermatt", "crans_montana", "lenzerheide",
    "arosa", "parsenn", "jakobshorn", "klosters",
    "ischgl", "lech", "zuers", "st_johann_in_tirol",
    "serfaus_fiss_ladis", "obergurgl_hochgurgl", "hintertux",
    "mayrhofen", "zell_am_see", "kaprun", "saalbach",
    "hinterglemm", "lofer", "hochkonig", "flachau",
    "wagrain", "obertauern", "schladming", "ramsau",
}

resorts = json.loads(PATH.read_text(encoding="utf-8"))

for r in resorts:
    if r.get("source") == "curated_seed":
        r["venue_type"] = "resort"
    elif r["id"] in KNOWN_RESORTS:
        r["venue_type"] = "resort"
    elif r.get("bounds"):
        # Estimate size: if area > ~5km x 5km → probably a real resort
        b = r["bounds"]
        lat_km = (b["max_lat"] - b["min_lat"]) * 111
        lon_km = (b["max_lon"] - b["min_lon"]) * 111 * 0.7
        if lat_km > 3 and lon_km > 3:
            r["venue_type"] = "resort"
        else:
            r["venue_type"] = "ski_area"
    else:
        r["venue_type"] = "ski_area"

resorts_count  = sum(1 for r in resorts if r["venue_type"] == "resort")
ski_area_count = sum(1 for r in resorts if r["venue_type"] == "ski_area")

PATH.write_text(json.dumps(resorts, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"סיום! {resorts_count} ריזורטים | {ski_area_count} אתרי סקי | סה\"כ {len(resorts)}")