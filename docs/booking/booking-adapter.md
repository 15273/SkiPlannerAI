# Booking adapter (future phase)

## Problem

Live hotel/package prices usually require **partner agreements**, strict display rules, and short TTLs. The MVP must not promise “real-time booking” without a provider contract.

## Design hook

Introduce a small port/adapter boundary in the backend (language-agnostic concept):

```text
BookingAdapter
  search_stays(query) -> list[RateQuote]
  resolve_checkout_url(quote_id) -> URL
```

### RateQuote (conceptual model)

| Field | Purpose |
|-------|---------|
| `provider` | e.g. `noop`, `partner_x` |
| `external_offer_id` | Opaque id from partner |
| `title` | Hotel or package label |
| `currency` | ISO 4217 |
| `total_price` | Numeric; may be null if partner forbids display |
| `fetched_at` | UTC timestamp |
| `ttl_seconds` | Cache / display validity |
| `disclaimer` | Legal / “price on provider site” text |

### MVP implementation

- **`NoOpBookingAdapter`**: returns empty results; documents the seam for the team.
- **No user-facing booking UI** until a partner is selected and compliance reviewed.

## Integration notes (later)

- Prefer official **affiliate / B2B APIs** over scraping.
- Separate **search** (cached hints) from **checkout** (always on provider domain).
- Log rate-limit and ToS constraints per provider in `docs/booking/providers.md` (create when needed).
