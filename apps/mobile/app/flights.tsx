import { Stack, useLocalSearchParams } from 'expo-router';
import { FlightSearchScreen } from '../src/screens/FlightSearchScreen';

function normalizeParam(v: string | string[] | undefined): string | undefined {
  if (v == null) return undefined;
  const s = Array.isArray(v) ? v[0] : v;
  return typeof s === 'string' && s.length > 0 ? s : undefined;
}

export default function FlightsRoute() {
  const p = useLocalSearchParams<{ departure?: string; origin?: string; destination?: string }>();
  const departureRaw = normalizeParam(p.departure);
  const departure =
    departureRaw != null && /^\d{4}-\d{2}-\d{2}$/.test(departureRaw) ? departureRaw : undefined;
  const origin = normalizeParam(p.origin) ?? '';
  const destination = normalizeParam(p.destination) ?? '';

  return (
    <>
      <Stack.Screen options={{ title: 'Flights' }} />
      <FlightSearchScreen
        defaultOrigin={origin}
        defaultDestination={destination}
        defaultDepartureIso={departure ?? ''}
      />
    </>
  );
}
