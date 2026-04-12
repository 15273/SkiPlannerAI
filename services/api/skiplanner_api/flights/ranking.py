from __future__ import annotations

from typing import Any

from ..models import FlightSearchRequest, RankedFlightOffer


def _offer_price_eur(offer: dict[str, Any]) -> float | None:
    try:
        price = offer["price"]["grandTotal"]
        return float(price)
    except (KeyError, TypeError, ValueError):
        return None


def _offer_duration_minutes(offer: dict[str, Any]) -> int | None:
    try:
        itins = offer.get("itineraries") or []
        if not itins:
            return None
        total = itins[0].get("duration", "")
        # PT2H30M
        if not total.startswith("PT"):
            return None
        hours = 0
        minutes = 0
        rest = total[2:]
        if "H" in rest:
            h, rest = rest.split("H", 1)
            hours = int(h)
        if rest.endswith("M"):
            minutes = int(rest[:-1])
        return hours * 60 + minutes
    except (ValueError, TypeError):
        return None


def _offer_stops(offer: dict[str, Any]) -> int | None:
    try:
        itins = offer.get("itineraries") or []
        if not itins:
            return None
        segs = itins[0].get("segments") or []
        return max(0, len(segs) - 1)
    except (TypeError, ValueError):
        return None


def _carrier_summary(offer: dict[str, Any]) -> str | None:
    try:
        itins = offer.get("itineraries") or []
        if not itins:
            return None
        carriers: list[str] = []
        for seg in itins[0].get("segments") or []:
            c = (seg.get("carrierCode") or "").strip()
            if c:
                carriers.append(c)
        return "+".join(dict.fromkeys(carriers)) if carriers else None
    except (TypeError, ValueError):
        return None


def rank_offers(
    offers: list[dict[str, Any]],
    req: FlightSearchRequest,
    top_n: int = 5,
) -> list[RankedFlightOffer]:
    scored: list[tuple[float, dict[str, Any], str]] = []
    for o in offers:
        price = _offer_price_eur(o)
        duration = _offer_duration_minutes(o)
        stops = _offer_stops(o)
        if req.max_stops is not None and stops is not None and stops > req.max_stops:
            continue
        if req.budget_eur is not None and price is not None and price > req.budget_eur:
            continue

        if req.prefer == "cheapest":
            if price is None:
                continue
            score = price
            reason = "Cheapest within filters"
        elif req.prefer == "fastest":
            if duration is None:
                continue
            score = float(duration)
            reason = "Shortest travel time within filters"
        else:
            norm_price = price if price is not None else 10_000.0
            norm_dur = float(duration) if duration is not None else 24 * 60.0
            norm_stops = float(stops) if stops is not None else 2.0
            score = norm_price * 0.6 + norm_dur * 1.2 + norm_stops * 180.0
            reason = "Balanced price, duration, and stops"

        scored.append((score, o, reason))

    scored.sort(key=lambda x: x[0])
    out: list[RankedFlightOffer] = []
    for idx, (_score, o, reason) in enumerate(scored[:top_n]):
        oid = str(o.get("id", "")) or f"offer_{idx}"
        out.append(
            RankedFlightOffer(
                id=oid,
                price_total_eur=_offer_price_eur(o),
                duration_minutes=_offer_duration_minutes(o),
                num_stops=_offer_stops(o),
                carrier_summary=_carrier_summary(o),
                raw=o if len(str(o)) < 50_000 else None,
                rank_reason=reason,
            )
        )
    return out


def skyscanner_deep_link(
    origin_iata: str,
    dest_iata: str,
    departure_date: str,
) -> str:
    """Deep link to Skyscanner (user completes booking on provider site)."""
    y, m, d = departure_date.split("-")
    path_date = f"{y}{m}{d}"
    o = origin_iata.upper()
    dst = dest_iata.upper()
    return f"https://www.skyscanner.net/transport/flights/{o}/{dst}/{path_date}/"
