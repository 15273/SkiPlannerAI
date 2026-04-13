import { useLocalSearchParams } from 'expo-router';
import { ResortDetailScreen } from '../../src/screens/ResortDetailScreen';

export default function ResortDetailRoute() {
  const { id } = useLocalSearchParams<{ id: string }>();
  return <ResortDetailScreen resortId={id ?? ''} />;
}
