import DateTimePicker, { type DateTimePickerEvent } from '@react-native-community/datetimepicker';
import { useEffect, useState } from 'react';
import {
  Modal,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { Colors, Radius, Spacing, Typography } from '../constants/theme';
import { SimpleMonthCalendar } from './SimpleMonthCalendar';

/** Local calendar date as YYYY-MM-DD (no UTC shift for calendar day). */
export function toIsoDateString(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function parseIsoToLocalDate(iso: string | null): Date {
  if (iso != null && /^\d{4}-\d{2}-\d{2}$/.test(iso)) {
    const [y, mo, da] = iso.split('-').map(Number);
    return new Date(y, mo - 1, da, 12, 0, 0, 0);
  }
  const t = new Date();
  t.setHours(12, 0, 0, 0);
  return t;
}

function startOfToday(): Date {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  return d;
}

type Props = {
  valueIso: string | null;
  onChange: (iso: string) => void;
  minimumDate?: Date;
  placeholder?: string;
};

export function DatePickerField({
  valueIso,
  onChange,
  minimumDate = startOfToday(),
  placeholder = 'Select date',
}: Props) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState(() => parseIsoToLocalDate(valueIso));

  useEffect(() => {
    if (open) setDraft(parseIsoToLocalDate(valueIso));
  }, [open, valueIso]);

  const label = valueIso ?? placeholder;

  const applySelection = () => {
    onChange(toIsoDateString(draft));
    setOpen(false);
  };

  const onAndroidChange = (event: DateTimePickerEvent, date?: Date) => {
    setOpen(false);
    if (event.type === 'set' && date != null) {
      onChange(toIsoDateString(date));
    }
  };

  const sheetCalendar = (
    <>
      <SimpleMonthCalendar
        selectedDate={draft}
        minimumDate={minimumDate}
        onSelectDay={(d) => setDraft(d)}
      />
      <View style={styles.sheetActions}>
        <Pressable style={styles.secondaryBtn} onPress={() => setOpen(false)}>
          <Text style={styles.secondaryLabel}>Cancel</Text>
        </Pressable>
        <Pressable style={styles.primaryBtn} onPress={applySelection}>
          <Text style={styles.primaryLabel}>Done</Text>
        </Pressable>
      </View>
    </>
  );

  return (
    <>
      <Pressable
        style={styles.field}
        onPress={() => setOpen(true)}
        accessibilityRole="button"
        accessibilityLabel="Open calendar to choose date"
        accessibilityValue={valueIso != null ? { text: valueIso } : undefined}
      >
        <Text style={[styles.fieldText, valueIso == null && styles.placeholder]}>{label}</Text>
        <Text style={styles.hint}>Tap to open calendar</Text>
      </Pressable>

      {Platform.OS === 'ios' && (
        <Modal visible={open} transparent animationType="slide" onRequestClose={() => setOpen(false)}>
          <Pressable style={styles.backdrop} onPress={() => setOpen(false)}>
            <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
              <Text style={styles.sheetTitle}>Choose date</Text>
              {sheetCalendar}
            </Pressable>
          </Pressable>
        </Modal>
      )}

      {Platform.OS === 'android' && open && (
        <DateTimePicker
          value={parseIsoToLocalDate(valueIso)}
          mode="date"
          display="default"
          minimumDate={minimumDate}
          onChange={onAndroidChange}
        />
      )}

      {Platform.OS === 'web' && (
        <Modal visible={open} transparent animationType="fade" onRequestClose={() => setOpen(false)}>
          <Pressable style={styles.backdrop} onPress={() => setOpen(false)}>
            <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
              <Text style={styles.sheetTitle}>Choose date</Text>
              {sheetCalendar}
            </Pressable>
          </Pressable>
        </Modal>
      )}
    </>
  );
}

const styles = StyleSheet.create({
  field: {
    borderWidth: 1.5,
    borderColor: Colors.surface,
    borderRadius: Radius.button,
    padding: Spacing.md,
    backgroundColor: Colors.surface,
    marginBottom: Spacing.xs,
  },
  fieldText: { ...Typography.body, color: Colors.textPrimary },
  placeholder: { color: Colors.textSecondary },
  hint: { ...Typography.caption, color: Colors.textSecondary, marginTop: 4 },
  backdrop: {
    flex: 1,
    backgroundColor: 'rgba(15,23,42,0.72)',
    justifyContent: 'flex-end',
  },
  sheet: {
    backgroundColor: '#0f172a',
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    padding: Spacing.md,
    paddingBottom: Spacing.lg,
    borderWidth: 1,
    borderColor: Colors.surface,
  },
  sheetTitle: {
    ...Typography.body,
    color: Colors.textPrimary,
    fontWeight: '700',
    marginBottom: Spacing.sm,
    textAlign: 'center',
  },
  sheetActions: {
    flexDirection: 'row',
    gap: Spacing.sm,
    marginTop: Spacing.md,
  },
  primaryBtn: {
    flex: 1,
    backgroundColor: Colors.accent,
    borderRadius: Radius.button,
    padding: Spacing.md,
    alignItems: 'center',
  },
  primaryLabel: { ...Typography.body, color: '#0f172a', fontWeight: '700' },
  secondaryBtn: {
    flex: 1,
    borderRadius: Radius.button,
    padding: Spacing.md,
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: Colors.surface,
  },
  secondaryLabel: { ...Typography.body, color: Colors.textSecondary },
});
