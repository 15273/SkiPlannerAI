import { ActivityIndicator, FlatList, StyleSheet, Text, View } from 'react-native';
import { ResortCard } from '../components/ResortCard';
import { Colors, Spacing, Typography } from '../constants/theme';
import { useResorts } from '../hooks/useResorts';
import type { Resort } from '../services/api';

type Props = { onSelectResort: (resort: Resort) => void };

export function ResortListScreen({ onSelectResort }: Props) {
  const { resorts, loading, error } = useResorts();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>skiMate</Text>
      <Text style={styles.subtitle}>Find your perfect ski resort</Text>

      {loading && (
        <View style={styles.center}>
          <ActivityIndicator size="large" color={Colors.accent} />
          <Text style={styles.loadingText}>Loading resorts…</Text>
        </View>
      )}

      {!loading && error != null && (
        <View style={styles.center}>
          <Text style={styles.errorText}>Could not load resorts</Text>
          <Text style={styles.errorDetail}>{error}</Text>
        </View>
      )}

      {!loading && error == null && resorts.length === 0 && (
        <View style={styles.center}>
          <Text style={styles.emptyText}>No resorts available yet.</Text>
        </View>
      )}

      {!loading && error == null && resorts.length > 0 && (
        <FlatList
          data={resorts}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <ResortCard resort={item} onPress={() => onSelectResort(item)} />
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
    paddingTop: 56,
    paddingHorizontal: Spacing.md,
  },
  title: { ...Typography.title, color: Colors.textPrimary },
  subtitle: {
    ...Typography.caption,
    color: Colors.textSecondary,
    marginTop: Spacing.xs,
    marginBottom: Spacing.md,
  },
  center: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: Spacing.sm,
  },
  loadingText: { ...Typography.body, color: Colors.textSecondary },
  errorText: { ...Typography.body, color: Colors.error, fontWeight: '600' },
  errorDetail: { ...Typography.caption, color: Colors.textSecondary },
  emptyText: { ...Typography.body, color: Colors.textSecondary },
  list: { paddingBottom: Spacing.xl },
});
