# Booking API Provider Research

> Companion to `docs/booking/booking-adapter.md`.
> Researched: 2026-04-12. Re-evaluate terms annually or before production launch.

---

## 1. Booking.com Affiliate Partner Program

| Property | Detail |
|----------|--------|
| **API type** | Affiliate REST API (official) |
| **Endpoint base** | `https://distribution-xml.booking.com/2.0/` |
| **Commercial terms** | Commission-based — typically 25–40% of Booking.com's own commission; no upfront cost or monthly fee |
| **Application** | Required — apply at [booking.com/affiliate-program](https://www.booking.com/affiliate-program.html) |
| **Approval timeline** | Days to weeks; Booking.com reviews traffic source and site quality |
| **Rate limits** | Varies by affiliate tier; new accounts start at conservative limits, increase with proven volume |
| **Price TTL** | Per-session only — prices must not be cached across sessions; always treat as stale after the user's session ends |
| **Ski resort coverage** | Excellent — global inventory including Alpine resorts across Europe, North America, and Japan |

### Display compliance requirements

- Must display **"Powered by Booking.com"** attribution on any page showing rates.
- Must show a price accuracy disclaimer (e.g. "Prices shown are indicative. Final price confirmed on Booking.com").
- Deep-linking to checkout must land on Booking.com's own domain; no frame embedding of checkout flow.
- Reviews and star ratings sourced from the API must credit Booking.com.

### Integration notes

- Use the `hotels` and `availability` endpoints for search; `hoteldetails` for property pages.
- Affiliate link tracking requires appending the affiliate ID (`aid=`) to all checkout URLs — maps directly to `BookingAdapter.resolve_checkout_url()`.
- `RateQuote.ttl_seconds` should be set to `0` (session-scoped) to prevent accidental display of stale prices.

---

## 2. Amadeus Hotel Search API

| Property | Detail |
|----------|--------|
| **API type** | B2B REST API |
| **Provider** | Amadeus for Developers (same account as our existing flights integration) |
| **Endpoint** | `https://api.amadeus.com/v1/reference-data/locations/hotels/by-city` + `/v3/shopping/hotel-offers` |
| **Commercial terms** | Free test tier (sandbox); production pricing is per-API-call (pay-as-you-go or volume contract) |
| **Application** | No separate application — use existing Amadeus `client_id` / `client_secret` from the flights integration |
| **Rate limits** | Free tier: 2,000 requests/month shared across all Amadeus APIs; production limits negotiated per contract |
| **Price TTL** | Offers carry an `available` flag and expiry timestamp in the response; treat as valid only for the current shopping session |
| **Ski resort coverage** | Good — sourced from GDS hotel inventory (Amadeus GDS); broad coverage of resort towns, though boutique ski chalets may be missing |

### Key advantage

We already hold Amadeus credentials for the flight search feature. Adding hotel search requires zero additional contracts, credentials, or legal review — just enabling the `Hotel Search` product in the existing Amadeus self-service dashboard.

### Integration notes

- Two-step flow: (1) `Hotel List` call to get `hotelIds` near a resort, (2) `Hotel Offers` call with check-in/out dates to get `RateQuote`-compatible price data.
- `RateQuote.external_offer_id` = Amadeus `offerId`; `resolve_checkout_url` should redirect to the Amadeus deep-link or a partner OTA.
- Monitor shared rate-limit consumption — flights and hotel calls draw from the same monthly quota on the free tier.
- No mandatory "Powered by Amadeus" badge, but review current Amadeus API ToS before public launch.

---

## 3. GetYourGuide Partner API

| Property | Detail |
|----------|--------|
| **API type** | Affiliate API (activities and experiences) |
| **Endpoint base** | `https://api.getyourguide.com/` (partner access) |
| **Commercial terms** | Commission-based; free to join the affiliate program |
| **Application** | Apply via [getyourguide.com/partner](https://partner.getyourguide.com/) |
| **Rate limits** | Documented per partner tier; moderate limits suitable for MVP traffic |
| **Price TTL** | Activity prices are generally stable (day-level), but availability windows should not be cached more than a few hours |
| **Ski resort coverage** | N/A for accommodation; focused on **activities and experiences** |

### Relevance to SkiPlannerAI

GetYourGuide does not provide hotel accommodation. Its value is as a complementary data source for:

- Ski lessons (group and private instruction)
- Guided off-piste tours
- Snowshoe, snowmobile, and aprés-ski experiences
- Airport and resort transfer activities

This maps to a potential future `ActivityAdapter` rather than the `BookingAdapter` accommodation flow, but sharing the affiliate infrastructure is logical.

### Integration notes

- Search endpoint accepts lat/lng or destination string — ski resort names resolve well.
- `RateQuote.disclaimer` should note that the activity is fulfilled by a third-party operator.
- Commission is earned on completed bookings; track via GetYourGuide's provided tracking parameters on the checkout URL.

---

## 4. Expedia Partner Solutions (EPS) Rapid API

| Property | Detail |
|----------|--------|
| **API type** | B2B API for Online Travel Agencies (OTAs) |
| **Endpoint base** | `https://api.ean.com/v3/` |
| **Commercial terms** | Revenue share; requires a formal business contract with Expedia Group |
| **Application** | Not self-service — requires a business development conversation with Expedia Partner Solutions sales |
| **Rate limits** | High throughput, designed for OTA-scale traffic |
| **Price TTL** | Standard short TTL (session-level); strict display rules enforced contractually |
| **Ski resort coverage** | Excellent — Expedia inventory is global and deep |

### Assessment for SkiPlannerAI MVP

EPS Rapid is designed for established OTAs and travel businesses with significant transaction volume. The entry bar — formal contract, revenue commitments, legal review — makes it unsuitable for an MVP or early-stage product. Revisit once monthly booking volume justifies the commercial relationship.

---

## Recommendation

### Phase 1 (MVP / pre-launch): Amadeus Hotel API

Use the **Amadeus Hotel Search API** immediately. We already have credentials and an approved account from the flights integration. Enabling hotel search requires only activating the product in the Amadeus dashboard — no new contracts, no new legal review, no new API keys. The shared rate-limit (2,000 req/month free tier) is sufficient for internal testing and early beta users.

Implementation path:
1. Implement `AmadeusBookingAdapter` behind the existing `BookingAdapter` protocol.
2. Use the `Hotel List` + `Hotel Offers` endpoints.
3. Set `RateQuote.provider = "amadeus"` and respect offer expiry timestamps for `ttl_seconds`.
4. Monitor shared quota consumption across flights and hotel calls.

### Phase 2 (growth / post-PMF): Booking.com Affiliate

Once the product has demonstrated traffic and user intent, apply to the **Booking.com Affiliate Partner Program** for broader and deeper inventory, particularly for boutique alpine properties and non-GDS-listed ski chalets. The commission model means no fixed cost until bookings convert.

Implementation path:
1. Apply at [booking.com/affiliate-program](https://www.booking.com/affiliate-program.html).
2. Implement `BookingComAdapter` alongside (not replacing) the Amadeus adapter.
3. Add a provider-ranking or fallback strategy in `NoOpBookingAdapter`'s successor.
4. Ensure display compliance: "Powered by Booking.com" badge and price disclaimer.

### Future consideration: GetYourGuide

Add a `GetYourGuideActivityAdapter` (separate from `BookingAdapter`) to surface ski lessons and guided experiences. Low barrier to entry and directly relevant to the SkiPlannerAI trip-planning use case.

### Do not pursue now: Expedia Partner Solutions

Defer EPS until the business has OTA-scale transaction volume to justify the contract process.
