import { useEffect, useState } from 'react';
import type { FeatureCollection } from 'geojson';
import { fetchResort, fetchResortMap, type Resort } from '../services/api';

type UseResortResult = {
  resort: Resort | null;
  mapData: FeatureCollection | null;
  loading: boolean;
  error: string | null;
};

export function useResort(id: string): UseResortResult {
  const [resort, setResort] = useState<Resort | null>(null);
  const [mapData, setMapData] = useState<FeatureCollection | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([fetchResort(id), fetchResortMap(id)])
      .then(([resortData, geoData]) => {
        if (!cancelled) {
          setResort(resortData);
          setMapData(geoData);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled)
          setError(e instanceof Error ? e.message : 'Failed to load resort');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [id]);

  return { resort, mapData, loading, error };
}
