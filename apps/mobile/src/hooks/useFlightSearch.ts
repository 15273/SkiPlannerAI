import { useState } from 'react';
import { searchFlights, type FlightSearchRequest, type FlightSearchResponse } from '../services/api';

type UseFlightSearchResult = {
  result: FlightSearchResponse | null;
  loading: boolean;
  error: string | null;
  search: (req: FlightSearchRequest) => Promise<void>;
  reset: () => void;
};

export function useFlightSearch(): UseFlightSearchResult {
  const [result, setResult] = useState<FlightSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async (req: FlightSearchRequest) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await searchFlights(req);
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
  };

  return { result, loading, error, search, reset };
}
