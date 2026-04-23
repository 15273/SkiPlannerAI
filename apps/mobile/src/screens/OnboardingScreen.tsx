import Slider from '@react-native-community/slider';
import { useState } from 'react';
import {
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { DatePickerField } from '../components/DatePickerField';
import { OptionButton } from '../components/onboarding/OptionButton';
import { StepIndicator } from '../components/onboarding/StepIndicator';
import { Colors, Radius, Spacing, Typography } from '../constants/theme';
import {
  DEFAULT_PREFERENCES,
  type GroupSize,
  type SkillLevel,
  type UserPreferences,
} from '../types/preferences';

const TOTAL_STEPS = 5;

const NIGHTS_OPTIONS: Array<3 | 5 | 7 | 10 | 14> = [3, 5, 7, 10, 14];

type Props = { onComplete: (prefs: UserPreferences) => void };

export function OnboardingScreen({ onComplete }: Props) {
  const [step, setStep] = useState(1);
  const [prefs, setPrefs] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const update = <K extends keyof UserPreferences>(key: K, value: UserPreferences[K]) =>
    setPrefs((p) => ({ ...p, [key]: value }));

  const canAdvance = (): boolean => {
    switch (step) {
      case 1: return prefs.skillLevel != null;
      case 2: return prefs.groupSize != null;
      case 3: return true; // budget always has a default
      case 4: return prefs.departureDateIso != null && prefs.nights != null;
      case 5: return prefs.originIata.length === 3;
      default: return false;
    }
  };

  const next = () => {
    if (step < TOTAL_STEPS) setStep((s) => s + 1);
    else onComplete(prefs);
  };

  const back = () => setStep((s) => Math.max(1, s - 1));

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView
        style={styles.container}
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <StepIndicator current={step} total={TOTAL_STEPS} />

        {/* Step 1: Skill level */}
        {step === 1 && (
          <View>
            <Text style={styles.heading}>What's your ski level?</Text>
            <Text style={styles.sub}>We'll match you with suitable resorts.</Text>
            {([
              { value: 'beginner', label: 'Beginner — I stick to easy slopes' },
              { value: 'intermediate', label: 'Intermediate — I handle blue & red runs' },
              { value: 'advanced', label: 'Advanced — blacks and off-piste' },
            ] as Array<{ value: SkillLevel; label: string }>).map(({ value, label }) => (
              <OptionButton
                key={value}
                label={label}
                selected={prefs.skillLevel === value}
                onPress={() => update('skillLevel', value)}
              />
            ))}
          </View>
        )}

        {/* Step 2: Group size */}
        {step === 2 && (
          <View>
            <Text style={styles.heading}>Who are you travelling with?</Text>
            <Text style={styles.sub}>Helps us suggest family-friendly or après-ski resorts.</Text>
            {([
              { value: 'solo', label: 'Just me' },
              { value: 'couple', label: 'Couple' },
              { value: 'small', label: 'Small group (3–5)' },
              { value: 'large', label: 'Large group (6+)' },
            ] as Array<{ value: GroupSize; label: string }>).map(({ value, label }) => (
              <OptionButton
                key={value}
                label={label}
                selected={prefs.groupSize === value}
                onPress={() => update('groupSize', value)}
              />
            ))}
          </View>
        )}

        {/* Step 3: Budget */}
        {step === 3 && (
          <View>
            <Text style={styles.heading}>What's your budget?</Text>
            <Text style={styles.sub}>Per person, including flights and accommodation.</Text>
            <Text style={styles.budgetDisplay}>€{prefs.budgetEur.toLocaleString()}</Text>
            <Slider
              style={styles.slider}
              minimumValue={200}
              maximumValue={3000}
              step={50}
              value={prefs.budgetEur}
              onValueChange={(v) => update('budgetEur', Math.round(v))}
              minimumTrackTintColor={Colors.accent}
              maximumTrackTintColor={Colors.surface}
              thumbTintColor={Colors.accent}
              accessibilityLabel="Budget slider"
              accessibilityHint={`Currently €${prefs.budgetEur}`}
            />
            <View style={styles.sliderLabels}>
              <Text style={styles.sliderLabel}>€200</Text>
              <Text style={styles.sliderLabel}>€3,000</Text>
            </View>
          </View>
        )}

        {/* Step 4: Dates */}
        {step === 4 && (
          <View>
            <Text style={styles.heading}>When do you want to go?</Text>
            <Text style={styles.sub}>Pick your preferred departure date from the calendar.</Text>
            <DatePickerField
              valueIso={prefs.departureDateIso}
              onChange={(iso) => update('departureDateIso', iso)}
            />

            <Text style={[styles.sub, { marginTop: Spacing.lg }]}>How many nights?</Text>
            <View style={styles.nightsRow}>
              {NIGHTS_OPTIONS.map((n) => (
                <Pressable
                  key={n}
                  style={[styles.nightBtn, prefs.nights === n && styles.nightBtnSelected]}
                  onPress={() => update('nights', n)}
                  accessibilityRole="radio"
                  accessibilityState={{ selected: prefs.nights === n }}
                  accessibilityLabel={`${n} nights`}
                >
                  <Text style={[styles.nightLabel, prefs.nights === n && styles.nightLabelSelected]}>
                    {n}
                  </Text>
                </Pressable>
              ))}
            </View>
          </View>
        )}

        {/* Step 5: Origin airport */}
        {step === 5 && (
          <View>
            <Text style={styles.heading}>Where do you fly from?</Text>
            <Text style={styles.sub}>Enter your nearest airport code (e.g. TLV, LHR, CDG).</Text>
            <TextInput
              style={styles.input}
              placeholder="TLV"
              placeholderTextColor={Colors.textSecondary}
              value={prefs.originIata}
              onChangeText={(t) => update('originIata', t.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 3))}
              keyboardType="default"
              autoCapitalize="characters"
              maxLength={3}
              accessibilityLabel="Origin airport IATA code"
              accessibilityHint="Three-letter airport code"
            />
          </View>
        )}
      </ScrollView>

      {/* Bottom navigation */}
      <View style={styles.nav}>
        {step > 1 && (
          <Pressable style={styles.backBtn} onPress={back} accessibilityRole="button" accessibilityLabel="Go back">
            <Text style={styles.backLabel}>Back</Text>
          </Pressable>
        )}
        <Pressable
          style={[styles.nextBtn, !canAdvance() && styles.nextBtnDisabled]}
          onPress={next}
          disabled={!canAdvance()}
          accessibilityRole="button"
          accessibilityLabel={step === TOTAL_STEPS ? 'Find resorts' : 'Next step'}
          accessibilityState={{ disabled: !canAdvance() }}
        >
          <Text style={styles.nextLabel}>
            {step === TOTAL_STEPS ? 'Find Resorts' : 'Next →'}
          </Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: Colors.background },
  container: { flex: 1 },
  content: { padding: Spacing.lg, paddingTop: Spacing.xl },
  heading: { ...Typography.title, color: Colors.textPrimary, marginBottom: Spacing.xs },
  sub: { ...Typography.body, color: Colors.textSecondary, marginBottom: Spacing.md },
  budgetDisplay: {
    ...Typography.display,
    color: Colors.accent,
    textAlign: 'center',
    marginVertical: Spacing.md,
  },
  slider: { width: '100%', height: 40 },
  sliderLabels: { flexDirection: 'row', justifyContent: 'space-between' },
  sliderLabel: { ...Typography.caption, color: Colors.textSecondary },
  input: {
    borderWidth: 1.5,
    borderColor: Colors.surface,
    borderRadius: Radius.button,
    padding: Spacing.md,
    color: Colors.textPrimary,
    ...Typography.body,
    backgroundColor: Colors.surface,
    marginBottom: Spacing.xs,
  },
  nightsRow: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.sm },
  nightBtn: {
    width: 56, height: 56,
    borderRadius: Radius.card,
    borderWidth: 1.5, borderColor: Colors.surface,
    backgroundColor: Colors.surface,
    alignItems: 'center', justifyContent: 'center',
  },
  nightBtnSelected: { borderColor: Colors.accent, backgroundColor: 'rgba(56,189,248,0.12)' },
  nightLabel: { ...Typography.body, color: Colors.textSecondary },
  nightLabelSelected: { color: Colors.accent, fontWeight: '600' },
  nav: {
    flexDirection: 'row',
    padding: Spacing.md,
    gap: Spacing.sm,
    borderTopWidth: 1,
    borderTopColor: Colors.surface,
    backgroundColor: Colors.background,
  },
  backBtn: {
    flex: 1, paddingVertical: Spacing.md, borderRadius: Radius.button,
    borderWidth: 1.5, borderColor: Colors.surface,
    alignItems: 'center',
  },
  backLabel: { ...Typography.body, color: Colors.textSecondary },
  nextBtn: {
    flex: 2, paddingVertical: Spacing.md, borderRadius: Radius.button,
    backgroundColor: Colors.accent, alignItems: 'center',
  },
  nextBtnDisabled: { backgroundColor: Colors.surface },
  nextLabel: { ...Typography.body, color: '#0f172a', fontWeight: '700' },
});
