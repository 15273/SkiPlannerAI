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

    Logging policy: only status codes and timing metadata are logged.
    client_id, client_secret, and raw response bodies are never logged.
    """
    if not client_id or not client_secret:
        logger.warning(
            "Amadeus credentials not configured — skipping token fetch",
            extra={"event": "token_fetch_skipped", "category": NO_CREDENTIALS},
        )
        return None

    now = time.time()
    if _TOKEN_CACHE["token"] and now < _TOKEN_CACHE["expiry"] - 60:
        logger.debug(
            "Amadeus token served from cache (expires in %.0fs)",
            _TOKEN_CACHE["expiry"] - now,
            extra={"event": "token_cache_hit"},
        )
        return str(_TOKEN_CACHE["token"])

    url = f"https://{hostname}/v1/security/oauth2/token"
    t0 = time.monotonic()
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
            elapsed_ms = int((time.monotonic() - t0) * 1000)
            if r.status_code == 401:
                logger.error(
                    "Amadeus token endpoint returned HTTP 401 (elapsed=%dms)",
                    elapsed_ms,
                    extra={"event": "token_fetch_error", "http_status": 401, "category": AUTH_FAILED, "elapsed_ms": elapsed_ms},
                )
                raise AmadeusError(AUTH_FAILED, "Amadeus returned 401 on token request")
            r.raise_for_status()
            data = r.json()
    except httpx.TimeoutException as exc:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        logger.error(
            "Amadeus token request timed out (elapsed=%dms)",
            elapsed_ms,
            extra={"event": "token_fetch_timeout", "category": NETWORK_ERROR, "elapsed_ms": elapsed_ms},
        )
        raise AmadeusError(NETWORK_ERROR, "Timeout fetching Amadeus token") from exc
    except httpx.HTTPStatusError as exc:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        logger.error(
            "Amadeus token endpoint returned HTTP %d (elapsed=%dms)",
            exc.response.status_code,
            elapsed_ms,
            extra={"event": "token_fetch_error", "http_status": exc.response.status_code, "category": API_ERROR, "elapsed_ms": elapsed_ms},
        )
        raise AmadeusError(API_ERROR, f"Amadeus token error: {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        logger.error(
            "Amadeus network error during token fetch: %s (elapsed=%dms)",
            type(exc).__name__,
            elapsed_ms,
            extra={"event": "token_fetch_network_error", "exc_type": type(exc).__name__, "category": NETWORK_ERROR, "elapsed_ms": elapsed_ms},
        )
        raise AmadeusError(NETWORK_ERROR, f"Network error fetching Amadeus token: {type(exc).__name__}") from exc

    token = data.get("access_token")
    expires_in = float(data.get("expires_in", 1799))
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expiry"] = now + expires_in
    elapsed_ms = int((time.monotonic() - t0) * 1000)
    logger.info(
        "Amadeus token obtained successfully (expires_in=%.0fs, elapsed=%dms)",
        expires_in,
        elapsed_ms,
        extra={"event": "token_fetch_ok", "expires_in_s": int(expires_in), "elapsed_ms": elapsed_ms},
    )
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

    Logging policy:
    - Logs request metadata (adults count, departure date) and response metadata
      (offer count, HTTP status code, elapsed time).
    - Never logs: raw offer objects, passenger names, emails, passport numbers,
      or auth credentials.
    """
    t0 = time.monotonic()
    logger.debug(
        "Amadeus flight search request: adults=%d, departure_date=%s",
        adults,
        departure_date,
        extra={"event": "flight_search_request", "adults": adults, "departure_date": departure_date},
    )
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await _do_flight_search(client, hostname, token, origin, destination, departure_date, adults)
            elapsed_ms = int((time.monotonic() - t0) * 1000)

            if r.status_code == 429:
                logger.warning(
                    "Amadeus rate limit hit (HTTP 429, elapsed=%dms) — waiting 2s then retrying once",
                    elapsed_ms,
                    extra={"event": "flight_search_rate_limited", "attempt": 1, "http_status": 429, "elapsed_ms": elapsed_ms},
                )
                await asyncio.sleep(2)
                r = await _do_flight_search(client, hostname, token, origin, destination, departure_date, adults)
                elapsed_ms = int((time.monotonic() - t0) * 1000)

                if r.status_code == 429:
                    logger.warning(
                        "Amadeus rate limit persists after retry (HTTP 429, elapsed=%dms) — falling back to deep link",
                        elapsed_ms,
                        extra={"event": "flight_search_rate_limited", "attempt": 2, "http_status": 429, "elapsed_ms": elapsed_ms},
                    )
                    raise AmadeusError(RATE_LIMITED, "Amadeus rate-limited after retry")

            if r.status_code == 401:
                logger.error(
                    "Amadeus auth failure on flight search (HTTP 401, elapsed=%dms)",
                    elapsed_ms,
                    extra={"event": "flight_search_error", "http_status": 401, "category": AUTH_FAILED, "elapsed_ms": elapsed_ms},
                )
                raise AmadeusError(AUTH_FAILED, "Amadeus returned 401 on flight search")

            if r.status_code >= 500:
                logger.error(
                    "Amadeus upstream server error on flight search (HTTP %d, elapsed=%dms)",
                    r.status_code,
                    elapsed_ms,
                    extra={"event": "flight_search_error", "http_status": r.status_code, "category": API_ERROR, "elapsed_ms": elapsed_ms},
                )
                raise AmadeusError(API_ERROR, f"Amadeus 5xx error: {r.status_code}")

            if r.status_code >= 400:
                logger.error(
                    "Amadeus API error on flight search (HTTP %d, elapsed=%dms)",
                    r.status_code,
                    elapsed_ms,
                    extra={"event": "flight_search_error", "http_status": r.status_code, "category": API_ERROR, "elapsed_ms": elapsed_ms},
                )
                raise AmadeusError(API_ERROR, f"Amadeus API error: {r.status_code}")

            r.raise_for_status()
            data = r.json()

    except AmadeusError:
        raise
    except httpx.TimeoutException as exc:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        logger.warning(
            "Amadeus flight search timed out (elapsed=%dms) — falling back to deep link",
            elapsed_ms,
            extra={"event": "flight_search_timeout", "category": NETWORK_ERROR, "elapsed_ms": elapsed_ms},
        )
        raise AmadeusError(NETWORK_ERROR, "Timeout during Amadeus flight search") from exc
    except httpx.HTTPError as exc:
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        logger.error(
            "Amadeus network error during flight search: %s (elapsed=%dms)",
            type(exc).__name__,
            elapsed_ms,
            extra={"event": "flight_search_network_error", "exc_type": type(exc).__name__, "category": NETWORK_ERROR, "elapsed_ms": elapsed_ms},
        )
        raise AmadeusError(NETWORK_ERROR, f"Network error during Amadeus flight search: {type(exc).__name__}") from exc

    # Log only the offer count — never log raw offer objects (may contain PII such as
    # passenger names, emails, or passport numbers returned by some Amadeus endpoints)
    offers = list(data.get("data", []))
    elapsed_ms = int((time.monotonic() - t0) * 1000)
    logger.info(
        "Amadeus flight search completed: offer_count=%d, elapsed=%dms",
        len(offers),
        elapsed_ms,
        extra={"event": "flight_search_ok", "offer_count": len(offers), "elapsed_ms": elapsed_ms},
    )
    return offers
