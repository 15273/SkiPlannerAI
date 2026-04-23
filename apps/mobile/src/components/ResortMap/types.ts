import type { FeatureCollection } from 'geojson';
import type { Resort } from '../../services/api';

export type ResortMapProps = {
  resort: Resort;
  mapData: FeatureCollection | null;
};
