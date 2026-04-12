import time
from typing import Any

import httpx

_TOKEN_CACHE: dict[str, Any] = {"token": None, "expiry": 0.0}


async def get_access_token(client_id: str, client_secret: str, hostname: str) -> str | None:
    if not client_id or not client_secret:
        return None
    now = time.time()
    if _TOKEN_CACHE["token"] and now < _TOKEN_CACHE["expiry"] - 60:
        return str(_TOKEN_CACHE["token"])
    url = f"https://{hostname}/v1/security/oauth2/token"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        data = r.json()
    token = data.get("access_token")
    expires_in = float(data.get("expires_in", 1799))
    _TOKEN_CACHE["token"] = token
    _TOKEN_CACHE["expiry"] = now + expires_in
    return str(token) if token else None


async def search_flight_offers(
    hostname: str,
    token: str,
    origin: str,
    destination: str,
    departure_date: str,
    adults: int,
) -> list[dict[str, Any]]:
    url = f"https://{hostname}/v2/shopping/flight-offers"
    params = {
        "originLocationCode": origin.upper(),
        "destinationLocationCode": destination.upper(),
        "departureDate": departure_date,
        "adults": adults,
        "max": 20,
        "currencyCode": "EUR",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
        )
        if r.status_code == 429:
            raise httpx.HTTPStatusError("Rate limited", request=r.request, response=r)
        r.raise_for_status()
        data = r.json()
    return list(data.get("data", []))
