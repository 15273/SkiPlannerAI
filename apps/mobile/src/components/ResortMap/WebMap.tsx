import { Linking, Pressable, StyleSheet, Text } from 'react-native';
import { Colors, Spacing, Typography } from '../../constants/theme';
import type { ResortMapProps } from './types';

/** Web: react-native-maps is native-only; link out to OpenStreetMap. */
export function ResortMap({ resort }: ResortMapProps) {
  const url = `https://www.openstreetmap.org/?mlat=${resort.centroid_lat}&mlon=${resort.centroid_lon}#map=13/${resort.centroid_lat}/${resort.centroid_lon}`;
  return (
    <Pressable
      style={styles.placeholder}
      onPress={() => void Linking.openURL(url)}
      accessibilityRole="link"
      accessibilityLabel={`Open map of ${resort.name} in browser`}
    >
      <Text style={styles.title}>Map preview</Text>
      <Text style={styles.hint}>
        Native maps run on iOS and Android. On web, tap to open OpenStreetMap.
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  placeholder: {
    flex: 1,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    padding: Spacing.md,
    gap: Spacing.sm,
    minHeight: 280,
  },
  title: { ...Typography.body, color: Colors.textPrimary, fontWeight: '700' },
  hint: { ...Typography.caption, color: Colors.textSecondary, textAlign: 'center' },
});
