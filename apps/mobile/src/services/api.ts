import Constants from 'expo-constants';

const apiBase: string =
  (Constants.expoConfig?.extra as { apiBaseUrl?: string } | undefined)
    ?.apiBaseUrl ?? 'http://localhost:8000';

export type Resort = {
  id: string;
  name: string;
  country: string;
  centroid_lat: number;
  centroid_lon: number;
  difficulty_hint?: 'beginner' | 'intermediate' | 'advanced' | 'mixed' | null;
  nearest_airport_iata?: string | null;
};

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

export async function fetchResortMap(id: string): Promise<unknown> {
  const res = await fetch(`${apiBase}/resorts/${id}/map`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
