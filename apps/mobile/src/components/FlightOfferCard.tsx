import { StyleSheet, Text, View } from 'react-native';
import { Colors, Radius, Spacing, Typography } from '../constants/theme';
import type { RankedFlightOffer } from '../services/api';

// Map rank_reason identifiers to human-readable explanations
const RANK_REASON_LABELS: Record<string, string> = {
  cheapest: 'Lowest price',
  fastest: 'Shortest flight',
  balanced: 'Best value',
  fewest_stops: 'Fewest stops',
  direct: 'Direct flight',
  fallback: 'Based on available data',
};

function formatDuration(minutes: number | null): string {
  if (minutes == null) return '—';
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${h}h ${m}m`;
}

type Props = { offer: RankedFlightOffer; rank: number };

export function FlightOfferCard({ offer, rank }: Props) {
  const reasonLabel =
    RANK_REASON_LABELS[offer.rank_reason] ?? offer.rank_reason;

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.rankBadge}>
          <Text style={styles.rankText}>#{rank}</Text>
        </View>
        <View style={styles.reasonTag}>
          <Text style={styles.reasonText}>{reasonLabel}</Text>
        </View>
      </View>

      <View style={styles.details}>
        {offer.carrier_summary != null && (
          <Text style={styles.carrier}>{offer.carrier_summary}</Text>
        )}
        <View style={styles.metaRow}>
          <Text style={styles.metaItem}>
            {offer.duration_minutes != null ? formatDuration(offer.duration_minutes) : '—'}
          </Text>
          <Text style={styles.metaSep}>·</Text>
          <Text style={styles.metaItem}>
            {offer.num_stops === 0
              ? 'Direct'
              : offer.num_stops === 1
              ? '1 stop'
              : offer.num_stops != null
              ? `${offer.num_stops} stops`
              : '—'}
          </Text>
        </View>
      </View>

      {offer.price_total_eur != null ? (
        <View>
          <Text style={styles.price}>~€{offer.price_total_eur.toFixed(0)}</Text>
          <Text style={styles.priceNote}>Indicative — verify on provider</Text>
        </View>
      ) : (
        <Text style={styles.priceNA}>Price on provider site</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.card,
    padding: Spacing.md,
    marginBottom: Spacing.sm,
  },
  header: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm, marginBottom: Spacing.sm },
  rankBadge: {
    width: 28, height: 28, borderRadius: 14,
    backgroundColor: Colors.accent, alignItems: 'center', justifyContent: 'center',
  },
  rankText: { ...Typography.caption, color: '#0f172a', fontWeight: '700' },
  reasonTag: {
    backgroundColor: 'rgba(56,189,248,0.12)',
    borderRadius: Radius.button,
    paddingHorizontal: Spacing.sm,
    paddingVertical: 2,
  },
  reasonText: { ...Typography.caption, color: Colors.accent },
  details: { marginBottom: Spacing.sm },
  carrier: { ...Typography.body, color: Colors.textPrimary, fontWeight: '600', marginBottom: 2 },
  metaRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.xs },
  metaItem: { ...Typography.caption, color: Colors.textSecondary },
  metaSep: { ...Typography.caption, color: Colors.textSecondary },
  price: { ...Typography.title, color: Colors.textPrimary },
  priceNote: { ...Typography.caption, color: Colors.textSecondary, marginTop: 2 },
  priceNA: { ...Typography.body, color: Colors.textSecondary },
});
