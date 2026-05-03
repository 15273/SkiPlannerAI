"""Export resorts.json to a CSV for manual review."""
import json
import csv
from pathlib import Path

INPUT  = Path(__file__).parent.parent / "data" / "seed" / "resorts.json"
OUTPUT = Path(__file__).parent.parent / "data" / "seed" / "resorts_review.csv"

COUNTRY_NAMES = {
    "FR": "צרפת", "CH": "שווייץ", "AT": "אוסטריה", "IT": "איטליה",
    "DE": "גרמניה", "NO": "נורבגיה", "SE": "שוודיה", "ES": "ספרד",
    "AD": "אנדורה", "BG": "בולגריה", "SK": "סלובקיה", "PL": "פולין",
    "SI": "סלובניה", "CZ": "צ'כיה", "RO": "רומניה", "LI": "ליכטנשטיין",
}

resorts = json.loads(INPUT.read_text(encoding="utf-8"))

with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "לשמור? (כן/לא)",
        "שם",
        "מדינה",
        "רמת קושי",
        "שדה תעופה",
        "קואורדינטות (Google Maps)",
        "הערות",
        "id (לא לשנות)",
    ])
    for r in resorts:
        writer.writerow([
            "",                          # לשמור?
            r["name"],                   # שם
            COUNTRY_NAMES.get(r["country"], r["country"]),  # מדינה
            r.get("difficulty_hint", ""),# רמת קושי
            r.get("nearest_airport_iata", ""),  # שדה תעופה
            f"{r['centroid_lat']}, {r['centroid_lon']}",  # קואורדינטות
            "",                          # הערות
            r["id"],                     # id
        ])

print(f"נוצר קובץ: {OUTPUT}")
print(f"סה\"כ {len(resorts)} ריזורטים לבדיקה")