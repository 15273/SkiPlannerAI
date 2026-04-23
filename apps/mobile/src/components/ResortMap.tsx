import type { FeatureCollection } from 'geojson';
import { StyleSheet, Text, View } from 'react-native';
import { Colors, Radius, Spacing, Typography } from '../constants/theme';
import type { Resort } from '../services/api';

type Props = { resort: Resort; mapData: FeatureCollection | null };

/** Placeholder until an interactive map is wired (GeoJSON is already loaded). */
export function ResortMap({ resort, mapData }: Props) {
  const n = mapData?.features?.length ?? 0;
  return (
    <View style={styles.box} accessibilityLabel="Resort map area">
      <Text style={styles.title}>{resort.name}</Text>
      <Text style={styles.sub}>
        {n > 0 ? `${n} map features loaded — interactive map coming soon` : 'Trail geometry not available yet'}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  box: {
    flex: 1,
    backgroundColor: Colors.surface,
    borderRadius: Radius.card,
    padding: Spacing.md,
    justifyContent: 'center',
  },
  title: { ...Typography.body, color: Colors.textPrimary, fontWeight: '700', marginBottom: Spacing.xs },
  sub: { ...Typography.caption, color: Colors.textSecondary },
});
