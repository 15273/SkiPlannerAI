import { useEffect, useMemo, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Colors, Radius, Spacing, Typography } from '../constants/theme';

const WEEKDAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'] as const;

function startOfDay(d: Date): Date {
  const x = new Date(d);
  x.setHours(0, 0, 0, 0);
  return x;
}

function sameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

function monthFirstDay(y: number, m: number): Date {
  return new Date(y, m, 1, 12, 0, 0, 0);
}

type Props = {
  /** Currently chosen day (local). */
  selectedDate: Date;
  /** Earliest selectable calendar day (local midnight). */
  minimumDate: Date;
  onSelectDay: (d: Date) => void;
};

/**
 * Small month grid: prev/next month, weekday row, day cells.
 * Works on web, iOS, and Android (same RN primitives).
 */
export function SimpleMonthCalendar({ selectedDate, minimumDate, onSelectDay }: Props) {
  const min = startOfDay(minimumDate);
  const [cursorY, setCursorY] = useState(() => selectedDate.getFullYear());
  const [cursorM, setCursorM] = useState(() => selectedDate.getMonth());

  useEffect(() => {
    setCursorY(selectedDate.getFullYear());
    setCursorM(selectedDate.getMonth());
  }, [selectedDate]);

  const title = useMemo(
    () =>
      monthFirstDay(cursorY, cursorM).toLocaleDateString(undefined, {
        month: 'long',
        year: 'numeric',
      }),
    [cursorY, cursorM],
  );

  const firstDow = new Date(cursorY, cursorM, 1).getDay();
  const daysInMonth = new Date(cursorY, cursorM + 1, 0).getDate();

  const canPrev =
    cursorY > min.getFullYear() ||
    (cursorY === min.getFullYear() && cursorM > min.getMonth());

  const goPrev = () => {
    if (!canPrev) return;
    if (cursorM === 0) {
      setCursorM(11);
      setCursorY((y) => y - 1);
    } else {
      setCursorM((m) => m - 1);
    }
  };

  const goNext = () => {
    if (cursorM === 11) {
      setCursorM(0);
      setCursorY((y) => y + 1);
    } else {
      setCursorM((m) => m + 1);
    }
  };

  const cells: Array<{ day: number; date: Date; disabled: boolean }> = [];
  for (let i = 0; i < firstDow; i++) {
    cells.push({ day: 0, date: new Date(), disabled: true });
  }
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(cursorY, cursorM, day, 12, 0, 0, 0);
    const disabled = startOfDay(date).getTime() < min.getTime();
    cells.push({ day, date, disabled });
  }

  return (
    <View style={styles.wrap}>
      <View style={styles.header}>
        <Pressable
          onPress={goPrev}
          disabled={!canPrev}
          style={[styles.navBtn, !canPrev && styles.navBtnDisabled]}
          accessibilityRole="button"
          accessibilityLabel="Previous month"
        >
          <Text style={styles.navBtnText}>‹</Text>
        </Pressable>
        <Text style={styles.title}>{title}</Text>
        <Pressable
          onPress={goNext}
          style={styles.navBtn}
          accessibilityRole="button"
          accessibilityLabel="Next month"
        >
          <Text style={styles.navBtnText}>›</Text>
        </Pressable>
      </View>

      <View style={styles.weekRow}>
        {WEEKDAYS.map((w) => (
          <Text key={w} style={styles.weekday}>
            {w}
          </Text>
        ))}
      </View>

      <View style={styles.grid}>
        {cells.map((cell, idx) => {
          if (cell.day === 0) {
            return <View key={`e-${idx}`} style={styles.cell} />;
          }
          const selected = sameDay(cell.date, selectedDate);
          return (
            <Pressable
              key={cell.day}
              style={[
                styles.cell,
                selected && styles.cellSelected,
                cell.disabled && styles.cellDisabled,
              ]}
              disabled={cell.disabled}
              onPress={() => onSelectDay(cell.date)}
              accessibilityRole="button"
              accessibilityState={{ selected, disabled: cell.disabled }}
              accessibilityLabel={`${cell.day}`}
            >
              <Text
                style={[
                  styles.dayText,
                  selected && styles.dayTextSelected,
                  cell.disabled && styles.dayTextDisabled,
                ]}
              >
                {cell.day}
              </Text>
            </Pressable>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { width: '100%' },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: Spacing.sm,
  },
  title: {
    ...Typography.body,
    color: Colors.textPrimary,
    fontWeight: '700',
    flex: 1,
    textAlign: 'center',
  },
  navBtn: {
    width: 40,
    height: 40,
    borderRadius: Radius.button,
    backgroundColor: Colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    borderColor: Colors.surface,
  },
  navBtnDisabled: { opacity: 0.35 },
  navBtnText: { fontSize: 22, color: Colors.textPrimary, lineHeight: 24 },
  weekRow: {
    flexDirection: 'row',
    marginBottom: Spacing.xs,
  },
  weekday: {
    flex: 1,
    textAlign: 'center',
    ...Typography.caption,
    color: Colors.textSecondary,
    fontWeight: '600',
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  cell: {
    width: '14.2857%',
    minHeight: 40,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 2,
  },
  cellSelected: {
    backgroundColor: 'rgba(56,189,248,0.25)',
    borderRadius: Radius.button,
  },
  cellDisabled: { opacity: 0.28 },
  dayText: { ...Typography.body, color: Colors.textPrimary },
  dayTextSelected: { color: Colors.accent, fontWeight: '700' },
  dayTextDisabled: { color: Colors.textSecondary },
});
