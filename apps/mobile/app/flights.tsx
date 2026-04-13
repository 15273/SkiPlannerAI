import { Stack } from 'expo-router';
import { FlightSearchScreen } from '../src/screens/FlightSearchScreen';

export default function FlightsRoute() {
  return (
    <>
      <Stack.Screen options={{ title: 'Flights' }} />
      <FlightSearchScreen />
    </>
  );
}
