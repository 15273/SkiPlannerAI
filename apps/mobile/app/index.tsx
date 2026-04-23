import AsyncStorage from '@react-native-async-storage/async-storage';
import { Stack, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, View } from 'react-native';
import { ResortListScreen } from '../src/screens/ResortListScreen';
import type { Resort } from '../src/services/api';
import type { UserPreferences } from '../src/types/preferences';
import { Colors } from '../src/constants/theme';

const PREFS_KEY = '@skimate/preferences';

export default function HomeRoute() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    AsyncStorage.getItem(PREFS_KEY)
      .then((json) => {
        if (!json) {
          router.replace('/onboarding');
        }
      })
      .catch(() => {})
      .finally(() => setChecking(false));
  }, []);

  const handleSelect = (resort: Resort) => {
    router.push({ pathname: '/resort/[id]', params: { id: resort.id } });
  };

  const handleFlights = async () => {
    try {
      const json = await AsyncStorage.getItem(PREFS_KEY);
      if (!json) {
        router.push('/flights');
        return;
      }
      const prefs = JSON.parse(json) as UserPreferences;
      const q = new URLSearchParams();
      if (prefs.departureDateIso != null && prefs.departureDateIso.length > 0) {
        q.set('departure', prefs.departureDateIso);
      }
      if (prefs.originIata.length === 3) {
        q.set('origin', prefs.originIata);
      }
      const qs = q.toString();
      router.push(qs.length > 0 ? `/flights?${qs}` : '/flights');
    } catch {
      router.push('/flights');
    }
  };

  if (checking) {
    return (
      <View style={{ flex: 1, backgroundColor: Colors.background, alignItems: 'center', justifyContent: 'center' }}>
        <ActivityIndicator color={Colors.accent} />
      </View>
    );
  }

  return (
    <>
      <Stack.Screen options={{ title: 'skiMate' }} />
      <ResortListScreen onSelectResort={handleSelect} onFlights={handleFlights} />
    </>
  );
}
