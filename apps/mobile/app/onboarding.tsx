import { useRouter } from 'expo-router';
import { OnboardingScreen } from '../src/screens/OnboardingScreen';
import { usePreferences } from '../src/hooks/usePreferences';
import type { UserPreferences } from '../src/types/preferences';

export default function OnboardingRoute() {
  const router = useRouter();
  const { savePrefs } = usePreferences();

  const handleComplete = async (prefs: UserPreferences) => {
    await savePrefs(prefs);
    router.replace('/');
  };

  return <OnboardingScreen onComplete={handleComplete} />;
}
