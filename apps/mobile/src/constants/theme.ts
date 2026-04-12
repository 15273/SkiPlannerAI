export const Colors = {
  background: '#0f172a',
  surface: '#1e293b',
  textPrimary: '#f8fafc',
  textSecondary: '#94a3b8',
  accent: '#38bdf8',
  error: '#fca5a5',
  success: '#4ade80',
} as const;

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
} as const;

export const Radius = {
  card: 12,
  button: 8,
} as const;

export const Typography = {
  display: { fontSize: 28, fontWeight: '700' as const, lineHeight: 36 },
  title:   { fontSize: 20, fontWeight: '700' as const, lineHeight: 28 },
  body:    { fontSize: 16, fontWeight: '400' as const, lineHeight: 24 },
  caption: { fontSize: 13, fontWeight: '400' as const, lineHeight: 18 },
} as const;
