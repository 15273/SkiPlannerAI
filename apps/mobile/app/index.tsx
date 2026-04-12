import { useRouter } from 'expo-router';
import { ResortListScreen } from '../src/screens/ResortListScreen';
import type { Resort } from '../src/services/api';

export default function HomeRoute() {
  const router = useRouter();

  const handleSelect = (resort: Resort) => {
    router.push({ pathname: '/resort/[id]', params: { id: resort.id } });
  };

  return <ResortListScreen onSelectResort={handleSelect} />;
}
