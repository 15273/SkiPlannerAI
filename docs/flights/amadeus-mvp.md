# Amadeus flight search (MVP)

## Credentials

Register at Amadeus for Developers, create an app, and use the **test** API hostname (`test.api.amadeus.com`) for development.

Set in repo root `.env` (see [.env.example](../../.env.example)):

- `AMADEUS_CLIENT_ID`
- `AMADEUS_CLIENT_SECRET`
- `AMADEUS_HOSTNAME` (default `test.api.amadeus.com`)

## Behavior

- `POST /flights/search` calls **Flight Offers Search** v2 when credentials exist.
- Offers are **ranked in-process** (`cheapest` | `fastest` | `balanced`) with optional `budget_eur` and `max_stops` filters.
- Response always includes `deep_link_url` (Skyscanner) for manual continuation when the API is down, rate-limited, or unconfigured.

## Rate limits and errors

- HTTP **429** from Amadeus returns `200` with `warning` and empty `offers`, preserving the deep link (see [skiplanner_api/routers/flights.py](../../services/api/skiplanner_api/routers/flights.py)).
- Other upstream errors surface as **502** with a short detail string.

## Compliance

Follow Amadeus terms of use for caching, attribution, and production keys. Do not scrape airline sites for user-facing prices in the MVP.
