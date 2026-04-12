import { useEffect, useState } from 'react';
import { fetchResorts, type Resort } from '../services/api';

type UseResortsResult = {
  resorts: Resort[];
  loading: boolean;
  error: string | null;
};

export function useResorts(): UseResortsResult {
  const [resorts, setResorts] = useState<Resort[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetchResorts()
      .then((data) => {
        if (!cancelled) setResorts(data);
      })
      .catch((e: unknown) => {
        if (!cancelled)
          setError(e instanceof Error ? e.message : 'Failed to load resorts');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { resorts, loading, error };
}
