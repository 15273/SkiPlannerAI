import Constants from 'expo-constants';
import type { FeatureCollection } from 'geojson';

const apiBase: string =
  (Constants.expoConfig?.extra as { apiBaseUrl?: string } | undefined)
    ?.apiBaseUrl ?? 'http://localhost:8040';

export type Resort = {
  id: string;
  name: string;
  country: string;
  centroid_lat: number;
  centroid_lon: number;
  difficulty_hint?: 'beginner' | 'intermediate' | 'advanced' | 'mixed' | null;
  nearest_airport_iata?: string | null;
};

// Re-export for consumers
export type { FeatureCollection as GeoJSONFeatureCollection };

export async function fetchResorts(): Promise<Resort[]> {
  const res = await fetch(`${apiBase}/resorts`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<Resort[]>;
}

export async function fetchResort(id: string): Promise<Resort> {
  const res = await fetch(`${apiBase}/resorts/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<Resort>;
}

export async function fetchResortMap(id: string): Promise<FeatureCollection> {
  const res = await fetch(`${apiBase}/resorts/${id}/map`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<FeatureCollection>;
}

export type RankedFlightOffer = {
  id: string;
  price_total_eur: number | null;
  duration_minutes: number | null;
  num_stops: number | null;
  carrier_summary: string | null;
  rank_reason: string;
};

export type FlightSearchResponse = {
  offers: RankedFlightOffer[];
  deep_link_url: string;
  provider: 'amadeus' | 'none';
  warning: string | null;
};

export type FlightSearchRequest = {
  origin_iata: string;
  destination_iata: string;
  departure_date: string;
  adults?: number;
  max_stops?: number | null;
  budget_eur?: number | null;
  prefer?: 'cheapest' | 'fastest' | 'balanced';
};

export async function searchFlights(req: FlightSearchRequest): Promise<FlightSearchResponse> {
  const res = await fetch(`${apiBase}/flights/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<FlightSearchResponse>;
}
