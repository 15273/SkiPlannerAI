import asyncio
import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_TOKEN_CACHE: dict[str, Any] = {"token": None, "expiry": 0.0}

# ── Error category constants ─────────────────────────────────────────────────
NO_CREDENTIALS = "NO_CREDENTIALS"
AUTH_FAILED = "AUTH_FAILED"
RATE_LIMITED = "RATE_LIMITED"
API_ERROR = "API_ERROR"
NETWORK_ERROR = "NETWORK_ERROR"

_TIMEOUT = httpx.Timeout(10.0)


class AmadeusError(Exception):
    """Raised when Amadeus returns a classified error."""

    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category


async def get_access_token(client_id: str, client_secret: str, hostname: str) -> str | None:
    """Fetch (or return cached) Amadeus OAuth2 bearer token.

    Returns None when credentials are absent (NO_CREDENTIALS).
    Raises AmadeusError on auth failure or network problems.
    """
    if not client_id or not client_secret:
        logger.warning("Amadeus credentials not configured (%s)", NO_CREDENTIALS)
        return None

    now = time.time()
    if _TOKEN_CACHE["token"] and now < _TOKEN_CACHE["expiry"] - 60:
        return str(_TOKEN_CACHE["token"])

    url = f"https://{hostname}/v1/security/oauth2/token"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    # Never log client_secret
                    "client_secret": client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if r.status_code == 401:
                logger.error("Amadeus auth failed (%s): HTTP 401 from token endpoint", AUTH_FAILED)
                raise AmadeusError(AUTH_FAILED, "Amadeus returned 401 on token request")
            r.raise_for_status()
            data = r.json()
    except httpx.TimeoutException as exc:
        logger.error("Amadeus token request timed out (%s)", NETWORK_ERROR)
        raise AmadeusError(NETWORK_ERROR, "Timeout fetching Amadeus token") from exc
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Amadeus token endpoint returned HTTP %s (%s)",
            exc.response.status_code,
            API_ERROR,
        )
        raise AmadeusError(API_ERROR, f"Amadeus token error: {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        logger.error("Amadeus network error during token fetch (%s): %s", NETWORK_ERROR, type(exc).__name__)
        raise AmadeusError(NETWORK_ERROR, f"Network error fetching Amadeus token: {type(exc).__name__}") from exc

    token = data.get("access_token")
    expires_in = float(data.get("expires_in", 1799))
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expiry"] = now + expires_in
    return str(token) if token else None


async def _do_flight_search(
    client: httpx.AsyncClient,
    hostname: str,
    token: str,
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
) -> httpx.Response:
    """Execute a single flight-offers GET (no retry logic here)."""
    url = f"https://{hostname}/v2/shopping/flight-offers"
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
        "adults": adults,
        "max": 20,
        "currencyCode": "EUR",
    }
    # Authorization header is never logged (httpx does not log headers by default)
    return await client.get(
        url,
        params=params,
        headers={"Authorization": f"Bearer {token}"},
    )


async def search_flight_offers(
    hostname: str,
    token: str,
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
) -> list[dict[str, Any]]:
    """Search Amadeus flight offers with retry on 429, 10-second timeout.

    Raises AmadeusError with an appropriate category on failure.
    Never logs origin/destination or auth credentials.
    """
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await _do_flight_search(client, hostname, token, origin, destination, departure_date, adults)

            if r.status_code == 429:
                logger.warning(
                    "Amadeus rate limit hit (%s) — waiting 2 s then retrying once",
                    RATE_LIMITED,
                )
                await asyncio.sleep(2)
                r = await _do_flight_search(client, hostname, token, origin, destination, departure_date, adults)

                if r.status_code == 429:
                    logger.warning(
                        "Amadeus rate limit persists after retry (%s) — falling back to deep link only",
                        RATE_LIMITED,
                    )
                    raise AmadeusError(RATE_LIMITED, "Amadeus rate-limited after retry")

            if r.status_code == 401:
                logger.error("Amadeus auth failure on flight search (%s)", AUTH_FAILED)
                raise AmadeusError(AUTH_FAILED, "Amadeus returned 401 on flight search")

            if r.status_code >= 400:
                logger.error(
                    "Amadeus API error on flight search (%s): HTTP %s",
                    API_ERROR,
                    r.status_code,
                )
                raise AmadeusError(API_ERROR, f"Amadeus API error: {r.status_code}")

            r.raise_for_status()
            data = r.json()

    except AmadeusError:
        raise
    except httpx.TimeoutException as exc:
        logger.warning(
            "Amadeus flight search timed out (%s) — falling back to deep link only",
            NETWORK_ERROR,
        )
        raise AmadeusError(NETWORK_ERROR, "Timeout during Amadeus flight search") from exc
    except httpx.HTTPError as exc:
        logger.error(
            "Amadeus network error during flight search (%s): %s",
            NETWORK_ERROR,
            type(exc).__name__,
        )
        raise AmadeusError(NETWORK_ERROR, f"Network error during Amadeus flight search: {type(exc).__name__}") from exc

    offers = list(data.get("data", []))
    logger.info("Amadeus flight search returned %d offer(s)", len(offers))
    return offers
