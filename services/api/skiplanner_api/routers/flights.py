import httpx
from fastapi import APIRouter, HTTPException

from ..config import settings
from ..flights.amadeus import get_access_token, search_flight_offers
from ..flights.ranking import rank_offers, skyscanner_deep_link
from ..models import FlightSearchRequest, FlightSearchResponse

router = APIRouter(prefix="/flights", tags=["flights"])


@router.post("/search", response_model=FlightSearchResponse)
async def search_flights(body: FlightSearchRequest) -> FlightSearchResponse:
    deep_link = skyscanner_deep_link(
        body.origin_iata, body.destination_iata, body.departure_date
    )
    warning: str | None = None

    token = await get_access_token(
        settings.amadeus_client_id,
        settings.amadeus_client_secret,
        settings.amadeus_hostname,
    )
    if not token:
        return FlightSearchResponse(
            offers=[],
            deep_link_url=deep_link,
            provider="none",
            warning="Amadeus credentials not configured; use deep_link_url to search.",
        )

    try:
        raw_offers = await search_flight_offers(
            settings.amadeus_hostname,
            token,
            body.origin_iata,
            body.destination_iata,
            body.departure_date,
            body.adults,
        )
    except httpx.HTTPStatusError as e:
        if e.response is not None and e.response.status_code == 429:
            return FlightSearchResponse(
                offers=[],
                deep_link_url=deep_link,
                provider="amadeus",
                warning="Amadeus rate limit reached; try again later or use deep_link_url.",
            )
        raise HTTPException(
            status_code=502,
            detail=f"Amadeus error: {e.response.status_code if e.response else 'unknown'}",
        ) from e
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e!s}") from e

    ranked = rank_offers(raw_offers, body)
    if not ranked and raw_offers:
        warning = "No offers matched filters; widen budget or stops."
    return FlightSearchResponse(
        offers=ranked,
        deep_link_url=deep_link,
        provider="amadeus",
        warning=warning,
    )
