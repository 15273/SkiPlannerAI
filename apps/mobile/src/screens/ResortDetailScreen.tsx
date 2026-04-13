import MapView, { Geojson, Marker, PROVIDER_DEFAULT } from 'react-native-maps';
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import type { FeatureCollection } from 'geojson';
import { Colors, Spacing, Typography, Radius } from '../constants/theme';
import { useResort } from '../hooks/useResort';

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: '#4ade80',
  intermediate: '#60a5fa',
  advanced: '#f87171',
  mixed: Colors.accent,
};

const DIFFICULTY_LABEL: Record<string, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
  mixed: 'Mixed',
};

type Props = { resortId: string };

export function ResortDetailScreen({ resortId }: Props) {
  const { resort, mapData, loading, error } = useResort(resortId);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={Colors.accent} />
        <Text style={styles.loadingText}>Loading resort…</Text>
      </View>
    );
  }

  if (error != null || resort == null) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>Could not load resort</Text>
        <Text style={styles.errorDetail}>{error ?? 'Unknown error'}</Text>
      </View>
    );
  }

  const region = {
    latitude: resort.centroid_lat,
    longitude: resort.centroid_lon,
    latitudeDelta: 0.08,
    longitudeDelta: 0.08,
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header */}
      <Text style={styles.name}>{resort.name}</Text>
      <View style={styles.metaRow}>
        <Text style={styles.country}>{resort.country}</Text>
        {resort.difficulty_hint != null && (
          <View
            style={[
              styles.difficultyBadge,
              { backgroundColor: DIFFICULTY_COLOR[resort.difficulty_hint] ?? Colors.accent },
            ]}
          >
            <Text style={styles.difficultyText}>
              {DIFFICULTY_LABEL[resort.difficulty_hint] ?? resort.difficulty_hint}
            </Text>
          </View>
        )}
      </View>

      {/* Map */}
      <View style={styles.mapContainer}>
        <MapView
          style={styles.map}
          provider={PROVIDER_DEFAULT}
          initialRegion={region}
          accessibilityLabel={`Map of ${resort.name}`}
        >
          <Marker
            coordinate={{ latitude: resort.centroid_lat, longitude: resort.centroid_lon }}
            title={resort.name}
            description={resort.country}
          />
          {mapData != null && mapData.features.length > 0 && (
            <Geojson
              geojson={mapData as FeatureCollection}
              strokeColor={Colors.accent}
              fillColor="rgba(56, 189, 248, 0.15)"
              strokeWidth={2}
            />
          )}
        </MapView>
        {mapData == null && (
          <View style={styles.mapOverlay}>
            <Text style={styles.mapOverlayText}>Trail map not available</Text>
          </View>
        )}
      </View>

      {resort.nearest_airport_iata != null && (
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Nearest airport</Text>
          <Text style={styles.infoValue}>{resort.nearest_airport_iata}</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.md, paddingBottom: Spacing.xl },
  center: {
    flex: 1,
    backgroundColor: Colors.background,
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.sm,
  },
  loadingText: { ...Typography.body, color: Colors.textSecondary },
  errorText: { ...Typography.body, color: Colors.error, fontWeight: '600' },
  errorDetail: { ...Typography.caption, color: Colors.textSecondary },
  name: { ...Typography.title, color: Colors.textPrimary, marginBottom: Spacing.xs },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.md },
  country: { ...Typography.caption, color: Colors.textSecondary },
  difficultyBadge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
    borderRadius: Radius.button,
  },
  difficultyText: { ...Typography.caption, color: '#0f172a', fontWeight: '600' },
  mapContainer: {
    height: 320,
    borderRadius: Radius.card,
    overflow: 'hidden',
    marginBottom: Spacing.md,
    position: 'relative',
  },
  map: { flex: 1 },
  mapOverlay: {
    position: 'absolute',
    bottom: Spacing.sm,
    left: Spacing.sm,
    backgroundColor: 'rgba(15,23,42,0.75)',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: Radius.button,
  },
  mapOverlayText: { ...Typography.caption, color: Colors.textSecondary },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.surface,
  },
  infoLabel: { ...Typography.body, color: Colors.textSecondary },
  infoValue: { ...Typography.body, color: Colors.textPrimary, fontWeight: '600' },
});
