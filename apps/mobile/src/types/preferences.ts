export type SkillLevel = 'beginner' | 'intermediate' | 'advanced';
export type GroupSize = 'solo' | 'couple' | 'small' | 'large';

export type UserPreferences = {
  skillLevel: SkillLevel | null;
  groupSize: GroupSize | null;
  budgetEur: number;
  departureDateIso: string | null;  // YYYY-MM-DD
  nights: 3 | 5 | 7 | 10 | 14;
  originIata: string;
};

export const DEFAULT_PREFERENCES: UserPreferences = {
  skillLevel: null,
  groupSize: null,
  budgetEur: 1000,
  departureDateIso: null,
  nights: 7,
  originIata: '',
};
