"""Populate price and operational data for major European resorts."""
import json
from pathlib import Path

PATH = Path(__file__).parent.parent / "data" / "seed" / "resorts.json"

# Maps OSM resort ID -> price data
# (price_tier, adult_day, child_day, adult_6day, child_6day,
#  ski_rental, snowboard_rental, helmet_rental,
#  opening_hours, peak_months, quiet_months,
#  ticket_url, website_url)
PRICES = {
    # ── FRANCE ──────────────────────────────────────────────────────
    "brevent_flegere_chamonix":
        ("premium", 65, 52, 330, 264, 35, 38, 8, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.compagniedumontblanc.fr/en/ski-passes",
         "https://www.chamonix.com"),
    "val_thorens":
        ("premium", 58, 44, 290, 218, 30, 33, 7, "09:00-17:00", "Dec-Feb", "Nov,Apr",
         "https://www.valthorens.com/en/ski-pass",
         "https://www.valthorens.com"),
    # Courchevel 1850 OSM ID — part of Les 3 Vallées
    "les_3_vallees":
        ("premium", 68, 54, 340, 272, 40, 44, 9, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.les3vallees.com/en/ski-pass",
         "https://www.les3vallees.com"),
    # Tignes + Val d'Isère share a lift area in OSM
    "tignes_val_d_isere":
        ("premium", 68, 54, 340, 272, 38, 42, 9, "08:30-17:00", "Dec-Feb", "Nov,Apr",
         "https://www.valdisere.com/en/ski-pass",
         "https://www.valdisere.com"),
    "alpe_d_huez_grand_domaine":
        ("mid", 55, 42, 275, 210, 28, 30, 7, "09:00-17:00", "Dec-Feb", "Mar-Apr",
         "https://www.alpedhuez.com/en/ski-pass",
         "https://www.alpedhuez.com"),
    "les_deux_alpes":
        ("mid", 50, 38, 250, 190, 26, 28, 6, "09:00-17:00", "Dec-Feb", "Mar-Apr",
         "https://www.les2alpes.com/en/ski-pass",
         "https://www.les2alpes.com"),
    "megeve":
        ("premium", 60, 46, 295, 225, 35, 38, 8, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.megeve.com/en/ski-pass",
         "https://www.megeve.com"),
    "les_gets_morzine":
        ("mid", 55, 42, 272, 208, 28, 30, 7, "09:00-17:00", "Dec-Feb", "Mar-Apr",
         "https://www.morzine.com/en/ski-pass",
         "https://www.morzine.com"),
    "flaine":
        ("mid", 50, 38, 248, 188, 25, 28, 6, "09:00-17:00", "Dec-Feb", "Mar-Apr",
         "https://www.flaine.com/en/ski-pass",
         "https://www.flaine.com"),
    "les_arcs":
        ("mid", 55, 42, 275, 210, 28, 30, 7, "09:00-17:00", "Dec-Feb", "Mar-Apr",
         "https://www.lesarcs.com/en/ski-pass",
         "https://www.lesarcs.com"),
    "la_plagne":
        ("mid", 53, 40, 265, 200, 28, 30, 7, "09:00-17:00", "Dec-Feb", "Mar-Apr",
         "https://www.la-plagne.com/en/ski-pass",
         "https://www.la-plagne.com"),

    # ── SWITZERLAND ─────────────────────────────────────────────────
    "4_vallees_verbier_la_tzoumaz_nendaz_veysonnaz_thyon":
        ("premium", 75, 55, 370, 275, 45, 50, 10, "09:00-16:30", "Dec-Feb", "Nov,Apr",
         "https://www.verbier.ch/en/ski-pass",
         "https://www.verbier.ch"),
    "zermatt_breuil_cervinia":
        ("premium", 95, 48, 470, 238, 50, 55, 10, "08:30-16:30", "Dec-Feb", "Apr-May",
         "https://www.zermatt.ch/en/ski-pass",
         "https://www.zermatt.ch"),
    "schatzalp_strela_davos_klosters":
        ("premium", 68, 34, 340, 170, 40, 44, 9, "08:30-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.davos.ch/en/ski-pass",
         "https://www.davos.ch"),
    # Jungfrau region = Grindelwald-Wengen area
    "grindelwald_wengen_kleine_scheidegg_mannlichen":
        ("premium", 65, 33, 325, 163, 38, 42, 9, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.jungfrau.ch/en/ski-pass",
         "https://www.jungfrau.ch"),
    "gstaad_saanen_rougemont":
        ("premium", 70, 35, 348, 175, 42, 46, 9, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.gstaad.ch/en/ski-pass",
         "https://www.gstaad.ch"),
    # Engadin / St. Moritz
    "samedan_st_moritz":
        ("premium", 82, 41, 408, 205, 50, 55, 10, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.engadin.ch/en/ski-pass",
         "https://www.engadin.ch"),
    "saas_fee":
        ("premium", 62, 31, 308, 155, 35, 38, 8, "08:30-16:30", "Dec-Feb", "year-round",
         "https://www.saas-fee.ch/en/ski-pass",
         "https://www.saas-fee.ch"),
    "laax":
        ("premium", 65, 33, 318, 160, 38, 42, 9, "08:30-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.laax.com/en/ski-pass",
         "https://www.laax.com"),

    # ── AUSTRIA ──────────────────────────────────────────────────────
    "st_anton_st_christoph_stuben":
        ("premium", 60, 30, 298, 149, 32, 35, 8, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.stantonamarlberg.com/en/ski-pass",
         "https://www.stantonamarlberg.com"),
    "silvretta_arena_ischgl_samnaun":
        ("premium", 58, 29, 290, 145, 30, 33, 7, "09:00-16:30", "Nov-Feb", "Mar-May",
         "https://www.ischgl.com/en/ski-pass",
         "https://www.ischgl.com"),
    # KitzSki = Kitzbühel + Kirchberg
    "kitzski":
        ("premium", 62, 31, 308, 154, 32, 35, 8, "08:30-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.kitzbuehel.com/en/ski-pass",
         "https://www.kitzbuehel.com"),
    # Sölden OSM id
    "solden":
        ("premium", 58, 29, 290, 145, 30, 33, 7, "09:00-16:30", "Oct-Feb", "Mar-May",
         "https://www.soelden.com/en/ski-pass",
         "https://www.soelden.com"),
    "mayrhofen_hippach":
        ("mid", 52, 26, 258, 129, 28, 30, 7, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.mayrhofen.at/en/ski-pass",
         "https://www.mayrhofen.at"),
    "ski_arlberg":
        ("premium", 65, 33, 323, 163, 35, 38, 8, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.lech-zuers.at/en/ski-pass",
         "https://www.lech-zuers.at"),
    "skicircus_saalbach_hinterglemm_leogang_fieberbrunn":
        ("mid", 55, 28, 272, 136, 28, 30, 7, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.saalbach.com/en/ski-pass",
         "https://www.saalbach.com"),
    "obertauern":
        ("mid", 53, 27, 264, 132, 26, 28, 6, "09:00-16:30", "Nov-Feb", "Mar-May",
         "https://www.obertauern.com/en/ski-pass",
         "https://www.obertauern.com"),
    # Zell am See — Schmittenhöhe is the main ski area
    "schmittenhohe_zell_am_see":
        ("mid", 50, 25, 248, 124, 25, 28, 6, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.zellamsee-kaprun.com/en/ski-pass",
         "https://www.zellamsee-kaprun.com"),

    # ── ITALY ────────────────────────────────────────────────────────
    "cortina_d_ampezzo":
        ("premium", 55, 28, 272, 136, 30, 33, 7, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.cortina.dolomiti.org/en/ski-pass",
         "https://www.cortina.dolomiti.org"),
    "val_gardena":
        ("mid", 52, 26, 258, 130, 28, 30, 7, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.valgardena.it/en/ski-pass",
         "https://www.valgardena.it"),
    "bormio_ski":
        ("mid", 42, 21, 210, 105, 25, 28, 6, "09:00-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.bormioski.eu/en/ski-pass",
         "https://www.bormioski.eu"),
    "livigno":
        ("mid", 38, 19, 188, 94, 22, 25, 6, "09:00-17:00", "Dec-Feb", "Mar-May",
         "https://www.livigno.eu/en/ski-pass",
         "https://www.livigno.eu"),
    "courmayeur":
        ("premium", 52, 26, 258, 130, 28, 30, 7, "08:30-16:30", "Dec-Feb", "Mar-Apr",
         "https://www.courmayeur.net/en/ski-pass",
         "https://www.courmayeur.net"),
    "campiglio_dolomiti_di_brenta":
        ("premium", 52, 26, 258, 130, 28, 30, 7, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.ski.it/en/ski-pass",
         "https://www.ski.it"),
    "kronplatz_plan_de_corones":
        ("mid", 48, 24, 238, 119, 25, 28, 6, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.kronplatz.com/en/ski-pass",
         "https://www.kronplatz.com"),

    # ── SCANDINAVIA ──────────────────────────────────────────────────
    "are":
        ("mid", 55, 28, 272, 136, 30, 33, 7, "09:00-16:00", "Jan-Feb", "Mar-Apr",
         "https://www.skistar.com/are/ski-passes",
         "https://www.skistar.com/are"),
    "trysil":
        ("mid", 48, 24, 238, 120, 28, 30, 7, "09:00-16:00", "Jan-Feb", "Nov,Apr",
         "https://www.trysil.com/en/ski-pass",
         "https://www.trysil.com"),
    "hemsedal_skisenter":
        ("mid", 45, 23, 225, 113, 25, 28, 6, "09:00-16:00", "Jan-Feb", "Nov,Apr",
         "https://www.hemsedal.com/en/ski-pass",
         "https://www.hemsedal.com"),

    # ── SPAIN / ANDORRA ──────────────────────────────────────────────
    "grandvalira":
        ("mid", 38, 22, 190, 112, 22, 25, 6, "09:00-17:00", "Dec-Feb", "Mar-Apr",
         "https://www.grandvalira.com/en/ski-pass",
         "https://www.grandvalira.com"),
    "pal_arinsal":
        ("budget", 32, 18, 158, 90, 20, 22, 5, "09:00-17:00", "Dec-Feb", "Mar",
         "https://www.vallnord.com/en/ski-pass",
         "https://www.vallnord.com"),
    "estacio_d_esqui_baqueira_beret":
        ("mid", 42, 21, 208, 105, 24, 26, 6, "09:00-17:00", "Dec-Feb", "Mar",
         "https://www.baqueira.es/en/ski-pass",
         "https://www.baqueira.es"),
    "estacion_de_esqui_y_montana_de_sierra_nevada":
        ("mid", 38, 19, 188, 95, 22, 25, 5, "09:00-17:00", "Dec-Feb", "Mar-May",
         "https://www.sierranevada.es/en/ski-pass",
         "https://www.sierranevada.es"),

    # ── EASTERN EUROPE ───────────────────────────────────────────────
    "bansko":
        ("budget", 35, 18, 175, 90, 18, 20, 5, "08:30-16:30", "Dec-Feb", "Mar",
         "https://www.banskoski.com/en/ski-pass",
         "https://www.banskoski.com"),
    "jasna_low_tatras":
        ("budget", 38, 19, 188, 95, 20, 22, 5, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.jasna.sk/en/ski-pass",
         "https://www.jasna.sk"),
    "chopok_jasna":
        ("budget", 38, 19, 188, 95, 20, 22, 5, "09:00-16:30", "Dec-Feb", "Mar",
         "https://www.jasna.sk/en/ski-pass",
         "https://www.jasna.sk"),
    "cos_opo_zakopane":
        ("budget", 22, 11, 110, 55, 15, 18, 4, "09:00-16:00", "Dec-Feb", "Mar",
         "https://www.kasprowy-wierch.pl/en",
         "https://www.zakopane.pl/en"),
}

resorts = json.loads(PATH.read_text(encoding="utf-8"))
updated = 0

for r in resorts:
    if r["id"] in PRICES:
        (tier, ad, ch, a6, c6, ski, sb, hel,
         hours, peak, quiet, turl, wurl) = PRICES[r["id"]]
        r["price_tier"]               = tier
        r["adult_day_pass_peak_eur"]  = ad
        r["child_day_pass_peak_eur"]  = ch
        r["adult_6day_pass_eur"]      = a6
        r["child_6day_pass_eur"]      = c6
        r["ski_rental_day_eur"]       = ski
        r["snowboard_rental_day_eur"] = sb
        r["helmet_rental_day_eur"]    = hel
        r["opening_hours"]            = hours
        r["peak_months"]              = peak
        r["quiet_months"]             = quiet
        r["ticket_url"]               = turl
        r["website_url"]              = wurl
        r["price_season"]             = "2025/26"
        updated += 1

PATH.write_text(json.dumps(resorts, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Updated {updated} resorts with prices + website links")
