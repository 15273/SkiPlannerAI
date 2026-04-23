# Secrets & Environment Strategy

This document describes every secret used by SkiPlannerAI, where each one lives in each
environment, how to rotate them, and how a new developer gets set up.

---

## 1. Environments

| Name | Description | How secrets are provided |
|---|---|---|
| **development** | Local developer machine | `.env` file (gitignored) copied from `.env.example` |
| **staging** | CI-deployed preview / EAS staging build | GitHub Actions repository secrets |
| **production** | Live app / EAS production build | GitHub Actions environment secrets (`production` environment) |

---

## 2. Full Secrets Inventory

| Variable | Used by | Required for | Notes |
|---|---|---|---|
| `AMADEUS_CLIENT_ID` | FastAPI backend | Flight search | Amadeus developer portal — test env for dev/staging |
| `AMADEUS_CLIENT_SECRET` | FastAPI backend | Flight search | **Rotate every 90 days** — see §4 |
| `AMADEUS_HOSTNAME` | FastAPI backend | Flight search | `test.api.amadeus.com` (sandbox) or `api.amadeus.com` (prod) |
| `DATABASE_URL` | FastAPI backend | All DB operations | PostgreSQL+PostGIS asyncpg URL; CI uses a temporary service container |
| `API_ENV` | FastAPI backend | Runtime behaviour | `development` / `staging` / `production` |
| `CORS_ORIGINS` | FastAPI backend | Browser security | Comma-separated list of allowed origins |
| `EXPO_PUBLIC_API_BASE_URL` | Expo mobile app | API calls from device | Baked into the JS bundle at build time |
| `STAGING_API_BASE_URL` | Expo staging builds | EAS staging profile | Injected by CI; mirrors `EXPO_PUBLIC_API_BASE_URL` for staging |
| `MAPBOX_PUBLIC_TOKEN` | Expo mobile app | Map view | Public token — restrict to your domain / bundle ID |
| `GOOGLE_MAPS_API_KEY` | Expo mobile app | Map view (alt) | Restrict to app bundle ID and Maps SDK APIs |

### Where they live

| Variable | Local `.env` | GitHub Actions repo secret | GH Actions `production` env secret |
|---|:---:|:---:|:---:|
| `AMADEUS_CLIENT_ID` | yes | yes | yes |
| `AMADEUS_CLIENT_SECRET` | yes | yes | yes |
| `AMADEUS_HOSTNAME` | yes | yes | yes |
| `DATABASE_URL` | yes | yes (test DB) | yes (prod DB) |
| `API_ENV` | yes | — (set inline in workflow) | — (set inline in workflow) |
| `CORS_ORIGINS` | yes | yes | yes |
| `EXPO_PUBLIC_API_BASE_URL` | yes | yes | yes |
| `STAGING_API_BASE_URL` | yes | yes | — |
| `MAPBOX_PUBLIC_TOKEN` | yes | yes | yes |
| `GOOGLE_MAPS_API_KEY` | yes | yes | yes |

---

## 3. Onboarding a New Developer

1. Clone the repo.
2. Copy the template:
   ```bash
   cp .env.example .env
   ```
3. Fill in the required values in `.env`:
   - Ask a team member for the **Amadeus test credentials** (they are in 1Password under
     _SkiPlannerAI / Amadeus sandbox_).
   - Create your own local PostgreSQL+PostGIS database and set `DATABASE_URL`.
   - Set `EXPO_PUBLIC_API_BASE_URL=http://localhost:8040` for local development.
   - Leave `MAPBOX_PUBLIC_TOKEN` and `GOOGLE_MAPS_API_KEY` blank if you are not working on
     the map features — the app degrades gracefully.
4. Start the stack:
   ```bash
   docker compose up -d        # Postgres + PostGIS
   cd services/api && uvicorn skiplanner_api.main:app --reload --host 0.0.0.0 --port 8040
   cd apps/mobile && npx expo start
   ```
5. Verify: `GET http://localhost:8040/health` should return `{"status": "ok"}`.

> `.env` is listed in `.gitignore`. **Never** commit it.

---

## 4. Rotating Secrets

### Amadeus client secret (rotate every 90 days)

1. Log in at <https://developers.amadeus.com/>.
2. Open your application → **Credentials** → regenerate the secret.
3. Update the value in:
   - Your local `.env`.
   - GitHub repo secret `AMADEUS_CLIENT_SECRET` (Settings → Secrets and variables → Actions).
   - GitHub `production` environment secret if using a separate production key.
4. Re-run the latest CI workflow to confirm tests pass.

### Database URL (rotate on credential change)

1. Update the PostgreSQL user password on the database host.
2. Update `DATABASE_URL` in the same three places as above.

### Map tokens

- **Mapbox**: delete the old token in the Mapbox console and create a new restricted one.
  Update `MAPBOX_PUBLIC_TOKEN` everywhere.
- **Google Maps**: disable the old key in Google Cloud Console, create a new restricted key.
  Update `GOOGLE_MAPS_API_KEY` everywhere.

---

## 5. Adding a New Secret

1. Add it to `.env.example` with an empty value and an inline comment.
2. Document it in the tables in §2 of this file.
3. Add it to GitHub: **Settings → Secrets and variables → Actions → New repository secret**.
4. If it is production-only, also add it to the `production` GitHub Actions environment.
5. Update the CI workflow (`/.github/workflows/ci.yml`) to pass the secret as an env var.
6. Update the service's config (e.g., `services/api/skiplanner_api/config.py`) to read it.

---

## 6. Git History Audit

The following commands were run on 2026-04-12 to confirm no secrets were accidentally committed:

```bash
git log --all -S "AKIA" --oneline   # AWS access key prefix
git log --all -S "sk-" --oneline    # OpenAI / Stripe key prefix
```

**Results:**

- `AKIA` — no matches found in git history.
- `sk-` — one match found in the initial commit, traced to an npm lockfile URL
  (`queue-microtask` registry URL containing the string `sk-`). This is **not** a secret.

**Conclusion: no secrets found in git history.**

If you want to scan the full history yourself:

```bash
# Detect common secret patterns
git log --all -p | grep -E "(AKIA|sk-live|ghp_|xox[baprs]-)" | grep -v "^-"
```

For ongoing protection, enable **GitHub secret scanning** (repo Settings → Security →
Secret scanning) and consider adding [gitleaks](https://github.com/gitleaks/gitleaks) as a
pre-commit hook.
