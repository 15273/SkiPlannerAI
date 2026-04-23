import MapView, { Geojson, Marker, PROVIDER_DEFAULT } from 'react-native-maps';
import { StyleSheet, Text, View } from 'react-native';
import type { FeatureCollection } from 'geojson';
import { Colors, Radius, Spacing, Typography } from '../../constants/theme';
import type { ResortMapProps } from './types';

export function ResortMap({ resort, mapData }: ResortMapProps) {
  const region = {
    latitude: resort.centroid_lat,
    longitude: resort.centroid_lon,
    latitudeDelta: 0.08,
    longitudeDelta: 0.08,
  };

  return (
    <>
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
        <View style={styles.overlay}>
          <Text style={styles.overlayText}>Trail map not available</Text>
        </View>
      )}
    </>
  );
}

const styles = StyleSheet.create({
  map: { flex: 1 },
  overlay: {
    position: 'absolute',
    bottom: Spacing.sm,
    left: Spacing.sm,
    backgroundColor: 'rgba(15,23,42,0.75)',
    paddingHorizontal: Spacing.sm,
    paddingVertical: 4,
    borderRadius: Radius.button,
  },
  overlayText: { ...Typography.caption, color: Colors.textSecondary },
});
