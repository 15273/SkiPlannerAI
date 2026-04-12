# CI / CD Secrets Reference

Secrets are managed as GitHub Actions repository secrets at:
`https://github.com/15273/SkiPlannerAI/settings/secrets/actions`

## Full secrets list

| Secret | Used by | Required for | Notes |
|--------|---------|-------------|-------|
| `AMADEUS_CLIENT_ID` | FastAPI backend | Flight search | Amadeus developer portal (test env) |
| `AMADEUS_CLIENT_SECRET` | FastAPI backend | Flight search | Rotate every 90 days |
| `EXPO_PUBLIC_API_BASE_URL` | Expo mobile | Staging builds | e.g. `https://api-staging.skimate.app` |
| `MAPBOX_PUBLIC_TOKEN` | Expo mobile | Map view | Public token — restrict to your domain |
| `GOOGLE_MAPS_API_KEY` | Expo mobile | Map view (alt) | Restrict to app bundle ID |

## Rules

1. **Never commit secrets to git.** All secrets live in `.env` locally (gitignored).
2. **Update `.env.example`** whenever a new secret is added — use a placeholder value.
3. **Staging secrets** are injected by GitHub Actions. Production secrets use a separate environment.
4. **Rotate `AMADEUS_CLIENT_SECRET`** every 90 days.

## Adding a new secret

1. Add it to `.env.example` with a placeholder.
2. Document it in this file.
3. Add it in GitHub: Settings → Secrets and variables → Actions → New repository secret.
4. Update the service's config to read the env var.
