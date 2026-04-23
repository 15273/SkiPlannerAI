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

## Terms of Service (ToS) requirements

The following obligations apply to any deployment of the Amadeus flight-search integration:

1. **Attribution in the UI** — Any screen or component that displays flight offers sourced from Amadeus must include visible attribution (e.g. "Powered by Amadeus"). Refer to the Amadeus brand guidelines for exact copy and logo usage.

2. **No caching offers beyond 24 hours** — Flight offer data (prices, availability, itineraries) must not be stored or served from a cache for more than 24 hours after retrieval. Stale data must be discarded and re-fetched. This applies to both server-side caches (Redis, database) and client-side caches (AsyncStorage, SQLite).

3. **Production keys require a separate Amadeus app registration** — The test-environment app credentials (`test.api.amadeus.com`) are **not** valid on the production Amadeus APIs (`api.amadeus.com`). Before going to production you must:
   - Register a new, production-specific app in the [Amadeus for Developers portal](https://developers.amadeus.com/).
   - Request production access from Amadeus (review process may take several days).
   - Store the resulting `AMADEUS_CLIENT_ID` and `AMADEUS_CLIENT_SECRET` exclusively in GitHub Actions secrets — never in `.env`, source code, or CI logs.
