"""Future booking port. See docs/booking/booking-adapter.md."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class RateQuote:
    provider: str
    external_offer_id: str
    title: str
    currency: str
    total_price: float | None
    fetched_at: str
    ttl_seconds: int
    disclaimer: str


class BookingAdapter(Protocol):
    def search_stays(self, query: dict) -> list[RateQuote]: ...

    def resolve_checkout_url(self, quote_id: str) -> str: ...


class NoOpBookingAdapter:
    """Placeholder until a partner API is integrated."""

    def search_stays(self, query: dict) -> list[RateQuote]:
        return []

    def resolve_checkout_url(self, quote_id: str) -> str:
        return ""
