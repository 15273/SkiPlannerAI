import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Colors, Radius, Spacing, Typography } from '../constants/theme';
import type { Resort } from '../services/api';

const DIFFICULTY_LABEL: Record<string, string> = {
  beginner: 'Beginner',
  intermediate: 'Intermediate',
  advanced: 'Advanced',
  mixed: 'Mixed',
};

type Props = { resort: Resort; onPress: () => void };

export function ResortCard({ resort, onPress }: Props) {
  return (
    <Pressable
      style={({ pressed }) => [styles.card, pressed && styles.pressed]}
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={`${resort.name}, ${resort.country}`}
      accessibilityHint="Opens resort details"
    >
      <Text style={styles.name}>{resort.name}</Text>
      <View style={styles.meta}>
        <Text style={styles.country}>{resort.country}</Text>
        {resort.difficulty_hint != null && (
          <Text style={styles.difficulty}>
            {DIFFICULTY_LABEL[resort.difficulty_hint] ?? resort.difficulty_hint}
          </Text>
        )}
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    padding: Spacing.md,
    borderRadius: Radius.card,
    marginBottom: Spacing.sm,
  },
  pressed: { opacity: 0.85 },
  name: { ...Typography.body, color: Colors.textPrimary, fontWeight: '600' },
  meta: { flexDirection: 'row', gap: Spacing.sm, marginTop: Spacing.xs },
  country: { ...Typography.caption, color: Colors.textSecondary },
  difficulty: { ...Typography.caption, color: Colors.accent },
});
