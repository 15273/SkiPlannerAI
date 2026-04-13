import { ActivityIndicator, Linking, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { useState } from 'react';
import { FlightOfferCard } from '../components/FlightOfferCard';
import { Colors, Radius, Spacing, Typography } from '../constants/theme';
import { useFlightSearch } from '../hooks/useFlightSearch';
import type { FlightSearchRequest } from '../services/api';

const PREFER_OPTIONS: Array<{ value: FlightSearchRequest['prefer']; label: string }> = [
  { value: 'balanced', label: 'Best value' },
  { value: 'cheapest', label: 'Cheapest' },
  { value: 'fastest', label: 'Fastest' },
];

type Props = {
  defaultOrigin?: string;
  defaultDestination?: string;
};

export function FlightSearchScreen({ defaultOrigin = '', defaultDestination = '' }: Props) {
  const [origin, setOrigin] = useState(defaultOrigin);
  const [destination, setDestination] = useState(defaultDestination);
  const [date, setDate] = useState('');
  const [prefer, setPrefer] = useState<FlightSearchRequest['prefer']>('balanced');
  const { result, loading, error, search } = useFlightSearch();

  const canSearch =
    origin.length === 3 && destination.length === 3 && /^\d{4}-\d{2}-\d{2}$/.test(date);

  const handleSearch = () => {
    if (!canSearch) return;
    void search({ origin_iata: origin, destination_iata: destination, departure_date: date, prefer });
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content} keyboardShouldPersistTaps="handled">
      <Text style={styles.heading}>Flight Search</Text>

      {/* Form */}
      <View style={styles.formRow}>
        <View style={styles.formField}>
          <Text style={styles.label}>From</Text>
          <TextInput
            style={styles.input}
            value={origin}
            onChangeText={(t) => setOrigin(t.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3))}
            placeholder="TLV"
            placeholderTextColor={Colors.textSecondary}
            autoCapitalize="characters"
            maxLength={3}
            accessibilityLabel="Origin airport"
          />
        </View>
        <View style={styles.formField}>
          <Text style={styles.label}>To</Text>
          <TextInput
            style={styles.input}
            value={destination}
            onChangeText={(t) => setDestination(t.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3))}
            placeholder="GNB"
            placeholderTextColor={Colors.textSecondary}
            autoCapitalize="characters"
            maxLength={3}
            accessibilityLabel="Destination airport"
          />
        </View>
      </View>

      <Text style={styles.label}>Departure date</Text>
      <TextInput
        style={styles.input}
        value={date}
        onChangeText={setDate}
        placeholder="YYYY-MM-DD"
        placeholderTextColor={Colors.textSecondary}
        keyboardType="numbers-and-punctuation"
        maxLength={10}
        accessibilityLabel="Departure date"
      />

      <Text style={[styles.label, { marginTop: Spacing.sm }]}>Sort by</Text>
      <View style={styles.preferRow}>
        {PREFER_OPTIONS.map(({ value, label }) => (
          <Pressable
            key={value}
            style={[styles.preferBtn, prefer === value && styles.preferBtnSelected]}
            onPress={() => setPrefer(value)}
            accessibilityRole="radio"
            accessibilityState={{ selected: prefer === value }}
            accessibilityLabel={label}
          >
            <Text style={[styles.preferLabel, prefer === value && styles.preferLabelSelected]}>
              {label}
            </Text>
          </Pressable>
        ))}
      </View>

      <Pressable
        style={[styles.searchBtn, !canSearch && styles.searchBtnDisabled]}
        onPress={handleSearch}
        disabled={!canSearch || loading}
        accessibilityRole="button"
        accessibilityLabel="Search flights"
        accessibilityState={{ disabled: !canSearch || loading }}
      >
        <Text style={styles.searchBtnLabel}>{loading ? 'Searching…' : 'Search Flights'}</Text>
      </Pressable>

      {/* Loading */}
      {loading && (
        <View style={styles.center}>
          <ActivityIndicator color={Colors.accent} size="large" />
          <Text style={styles.loadingText}>Searching for flights…</Text>
        </View>
      )}

      {/* Error */}
      {!loading && error != null && (
        <View style={styles.center}>
          <Text style={styles.errorText}>Search failed</Text>
          <Text style={styles.errorDetail}>{error}</Text>
        </View>
      )}

      {/* Results */}
      {!loading && result != null && (
        <View style={styles.results}>
          {/* Warning / provider notice */}
          {result.warning != null && (
            <View style={styles.warningBox}>
              <Text style={styles.warningText}>⚠ {result.warning}</Text>
            </View>
          )}
          {result.provider === 'none' && (
            <View style={styles.warningBox}>
              <Text style={styles.warningText}>Live prices unavailable — showing search link only</Text>
            </View>
          )}

          {/* Offer list */}
          {result.offers.length > 0 ? (
            <>
              <Text style={styles.resultCount}>{result.offers.length} offers found</Text>
              {result.offers.map((offer, i) => (
                <FlightOfferCard key={offer.id} offer={offer} rank={i + 1} />
              ))}
            </>
          ) : (
            <View style={styles.center}>
              <Text style={styles.emptyText}>No offers found for this route.</Text>
            </View>
          )}

          {/* Deep link — always prominent */}
          <Pressable
            style={styles.deepLinkBtn}
            onPress={() => void Linking.openURL(result.deep_link_url)}
            accessibilityRole="link"
            accessibilityLabel="Search on Skyscanner"
            accessibilityHint="Opens Skyscanner in your browser to verify and book"
          >
            <Text style={styles.deepLinkLabel}>Search on Skyscanner</Text>
            <Text style={styles.deepLinkSub}>Compare prices and book directly</Text>
          </Pressable>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: Colors.background },
  content: { padding: Spacing.md, paddingBottom: Spacing.xl },
  heading: { ...Typography.title, color: Colors.textPrimary, marginBottom: Spacing.md },
  formRow: { flexDirection: 'row', gap: Spacing.sm },
  formField: { flex: 1 },
  label: { ...Typography.caption, color: Colors.textSecondary, marginBottom: Spacing.xs },
  input: {
    backgroundColor: Colors.surface,
    borderRadius: Radius.button,
    padding: Spacing.sm + 2,
    color: Colors.textPrimary,
    ...Typography.body,
    marginBottom: Spacing.sm,
  },
  preferRow: { flexDirection: 'row', gap: Spacing.sm, marginBottom: Spacing.md },
  preferBtn: {
    flex: 1, padding: Spacing.sm, borderRadius: Radius.button,
    backgroundColor: Colors.surface, alignItems: 'center',
    borderWidth: 1.5, borderColor: Colors.surface,
  },
  preferBtnSelected: { borderColor: Colors.accent, backgroundColor: 'rgba(56,189,248,0.12)' },
  preferLabel: { ...Typography.caption, color: Colors.textSecondary },
  preferLabelSelected: { color: Colors.accent, fontWeight: '600' },
  searchBtn: {
    backgroundColor: Colors.accent, borderRadius: Radius.button,
    padding: Spacing.md, alignItems: 'center', marginBottom: Spacing.lg,
  },
  searchBtnDisabled: { backgroundColor: Colors.surface },
  searchBtnLabel: { ...Typography.body, color: '#0f172a', fontWeight: '700' },
  center: { alignItems: 'center', paddingVertical: Spacing.xl, gap: Spacing.sm },
  loadingText: { ...Typography.body, color: Colors.textSecondary },
  errorText: { ...Typography.body, color: Colors.error, fontWeight: '600' },
  errorDetail: { ...Typography.caption, color: Colors.textSecondary },
  results: { gap: Spacing.xs },
  warningBox: {
    backgroundColor: 'rgba(252, 165, 165, 0.1)',
    borderRadius: Radius.button,
    padding: Spacing.sm,
    marginBottom: Spacing.sm,
  },
  warningText: { ...Typography.caption, color: Colors.error },
  resultCount: { ...Typography.caption, color: Colors.textSecondary, marginBottom: Spacing.sm },
  emptyText: { ...Typography.body, color: Colors.textSecondary },
  deepLinkBtn: {
    marginTop: Spacing.md,
    backgroundColor: Colors.surface,
    borderRadius: Radius.card,
    padding: Spacing.md,
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: Colors.accent,
  },
  deepLinkLabel: { ...Typography.body, color: Colors.accent, fontWeight: '700' },
  deepLinkSub: { ...Typography.caption, color: Colors.textSecondary, marginTop: 4 },
});
