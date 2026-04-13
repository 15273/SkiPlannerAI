import { Pressable, StyleSheet, Text } from 'react-native';
import { Colors, Radius, Spacing, Typography } from '../../constants/theme';

type Props = {
  label: string;
  selected: boolean;
  onPress: () => void;
  accessibilityLabel?: string;
};

export function OptionButton({ label, selected, onPress, accessibilityLabel }: Props) {
  return (
    <Pressable
      style={[styles.btn, selected && styles.selected]}
      onPress={onPress}
      accessibilityRole="radio"
      accessibilityState={{ selected }}
      accessibilityLabel={accessibilityLabel ?? label}
    >
      <Text style={[styles.label, selected && styles.labelSelected]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    borderWidth: 1.5,
    borderColor: Colors.surface,
    borderRadius: Radius.button,
    paddingVertical: Spacing.sm + 2,
    paddingHorizontal: Spacing.md,
    marginBottom: Spacing.sm,
    backgroundColor: Colors.surface,
  },
  selected: {
    borderColor: Colors.accent,
    backgroundColor: 'rgba(56, 189, 248, 0.12)',
  },
  label: { ...Typography.body, color: Colors.textSecondary, textAlign: 'center' },
  labelSelected: { color: Colors.accent, fontWeight: '600' },
});
