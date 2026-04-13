import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..config import settings
from ..flights.amadeus import (
    AUTH_FAILED,
    NETWORK_ERROR,
    NO_CREDENTIALS,
    RATE_LIMITED,
    AmadeusError,
    get_access_token,
    search_flight_offers,
)
from ..flights.ranking import rank_offers, skyscanner_deep_link
from ..models import FlightSearchRequest, FlightSearchResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/flights", tags=["flights"])

# Human-readable fallback messages keyed by error category
_FALLBACK_WARNINGS: dict[str, str] = {
    NO_CREDENTIALS: "Amadeus credentials not configured; use deep_link_url to search.",
    AUTH_FAILED: "Amadeus authentication failed; use deep_link_url to search.",
    RATE_LIMITED: "Amadeus rate limit reached; try again later or use deep_link_url.",
    "API_ERROR": "Amadeus API error; use deep_link_url to search.",
    NETWORK_ERROR: "Amadeus unreachable (timeout or network error); use deep_link_url to search.",
}

# Categories that map to HTTP 502 Bad Gateway instead of a graceful 200 fallback
_GATEWAY_ERROR_CATEGORIES = {AUTH_FAILED, "API_ERROR"}


def _rate_limit_response(deep_link: str, category: str, exc: AmadeusError) -> FlightSearchResponse:
    """Return HTTP 200 with warning + deep_link_url when Amadeus rate-limits us (429)."""
    warning = f"[{category}] {_FALLBACK_WARNINGS.get(category, str(exc))}"
    logger.warning(
        "Amadeus rate limit (%s) — returning HTTP 200 with warning and deep link",
        category,
    )
    return FlightSearchResponse(
        offers=[],
        deep_link_url=deep_link,
        provider="amadeus",
        warning=warning,
    )


def _gateway_error_response(category: str, exc: AmadeusError) -> JSONResponse:
    """Return HTTP 502 for auth failures and upstream 5xx errors."""
    detail = f"[{category}] {_FALLBACK_WARNINGS.get(category, str(exc))}"
    logger.error(
        "Amadeus gateway error (%s) — returning HTTP 502: %s",
        category,
        detail,
    )
    return JSONResponse(status_code=502, content={"detail": detail})


@router.post("/search", response_model=FlightSearchResponse)
async def search_flights(body: FlightSearchRequest) -> FlightSearchResponse:
    deep_link = skyscanner_deep_link(
        body.origin_iata, body.destination_iata, body.departure_date
    )

    # ── Step 1: obtain token ─────────────────────────────────────────────────
    try:
        token = await get_access_token(
            settings.amadeus_client_id,
            settings.amadeus_client_secret,
            settings.amadeus_hostname,
        )
    except AmadeusError as exc:
        # 401 from token endpoint → 502
        if exc.category in _GATEWAY_ERROR_CATEGORIES:
            return _gateway_error_response(exc.category, exc)
        # Rate-limit or network error during token fetch → 200 with warning
        return FlightSearchResponse(
            offers=[],
            deep_link_url=deep_link,
            provider="none",
            warning=f"[{exc.category}] {_FALLBACK_WARNINGS.get(exc.category, str(exc))}",
        )

    if not token:
        # Credentials absent — get_access_token returned None (not an exception)
        return FlightSearchResponse(
            offers=[],
            deep_link_url=deep_link,
            provider="none",
            warning=f"[{NO_CREDENTIALS}] {_FALLBACK_WARNINGS[NO_CREDENTIALS]}",
        )

    # ── Step 2: search offers ────────────────────────────────────────────────
    try:
        raw_offers = await search_flight_offers(
            settings.amadeus_hostname,
            token,
            body.origin_iata,
            body.destination_iata,
            body.departure_date,
            body.adults,
        )
    except AmadeusError as exc:
        # 429 → HTTP 200 with warning + deep_link_url
        if exc.category == RATE_LIMITED:
            return _rate_limit_response(deep_link, exc.category, exc)
        # 401 or upstream 5xx → HTTP 502
        if exc.category in _GATEWAY_ERROR_CATEGORIES:
            return _gateway_error_response(exc.category, exc)
        # Network / other errors → 200 with warning
        logger.warning(
            "Flight search failed (%s) — returning deep link only", exc.category
        )
        return FlightSearchResponse(
            offers=[],
            deep_link_url=deep_link,
            provider="amadeus",
            warning=f"[{exc.category}] {_FALLBACK_WARNINGS.get(exc.category, str(exc))}",
        )

    # ── Step 3: rank and return ──────────────────────────────────────────────
    ranked = rank_offers(raw_offers, body)
    warning: str | None = None
    if not ranked and raw_offers:
        warning = "No offers matched filters; widen budget or stops."

    return FlightSearchResponse(
        offers=ranked,
        deep_link_url=deep_link,
        provider="amadeus",
        warning=warning,
    )
