import AsyncStorage from '@react-native-async-storage/async-storage';
import { useEffect, useState } from 'react';
import { DEFAULT_PREFERENCES, type UserPreferences } from '../types/preferences';

const STORAGE_KEY = '@skimate/preferences';

export function usePreferences() {
  const [prefs, setPrefs] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem(STORAGE_KEY)
      .then((json) => {
        if (json) setPrefs({ ...DEFAULT_PREFERENCES, ...JSON.parse(json) });
      })
      .catch(() => {})
      .finally(() => setLoaded(true));
  }, []);

  const savePrefs = async (next: UserPreferences) => {
    setPrefs(next);
    await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  };

  return { prefs, savePrefs, loaded };
}
