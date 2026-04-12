#!/usr/bin/env bash
# Create GitHub milestones and issues for skiMate MVP (repo SkiPlannerAI).
# Requires: gh CLI, auth (`gh auth login`), and permission on the repo.
set -euo pipefail
REPO="${1:-15273/SkiPlannerAI}"

milestones=(
  "mvp-0-foundation"
  "mvp-1-resort-data"
  "mvp-2-core-ux"
  "mvp-3-flights-lite"
  "future-booking-adapter"
)

for m in "${milestones[@]}"; do
  if gh api "repos/${REPO}/milestones" --jq '.[].title' 2>/dev/null | grep -Fxq "${m}"; then
    echo "Milestone exists: ${m}"
  else
    gh api --method POST "repos/${REPO}/milestones" -f title="${m}" -f state=open
  fi
done

create_issue() {
  local title="$1" body="$2" milestone="$3"
  gh issue create --repo "${REPO}" --title "${title}" --body "${body}" --milestone "${milestone}"
}

create_issue "Lock mobile stack and monorepo layout" $'Expo + FastAPI scaffold is in repo. Verify team agreement, document map provider keys in apps/mobile/README, and confirm CI secrets policy.\n\nRefs: docs/decisions/001-mobile-and-monorepo.md' "mvp-0-foundation"
create_issue "Dev/staging env and secrets" $'No secrets in git; use .env locally and GitHub Actions secrets. Add staging API URL for mobile builds.\n\nRefs: .env.example' "mvp-0-foundation"
create_issue "Location privacy policy" $'Define what we store, retention, and consent copy for group location (future sprint).' "mvp-0-foundation"

create_issue "SkiArea / trail models + OSM ingest spec" $'Implement Overpass or extract pipeline per docs/data/osm-ingest-spec.md; write first real OSM-backed GeoJSON for 1–2 resorts.' "mvp-1-resort-data"
create_issue "Seed 10–30 resorts QA" $'Follow docs/qa/resort-map-checklist.md; expand data/seed/maps/*.geojson as ingest matures.' "mvp-1-resort-data"
create_issue "Map API contract tests" $'Smoke tests for GET /resorts, /resorts/{id}, /resorts/{id}/map.\n\nRefs: docs/api/map-api.md' "mvp-1-resort-data"

create_issue "Onboarding questionnaire UI" $'Budget, dates, level, country → call recommendation endpoint (future) or static filter client-side.' "mvp-2-core-ux"
create_issue "Rule-based resort recommendations" $'Server or client rules using seed metadata (difficulty_hint, country, etc.).' "mvp-2-core-ux"
create_issue "In-app resort map view" $'Render GeoJSON from API; pick Mapbox/Google and add keys.' "mvp-2-core-ux"

create_issue "Amadeus integration hardening" $'Production keys, error taxonomy, logging without PII.\n\nRefs: docs/flights/amadeus-mvp.md' "mvp-3-flights-lite"
create_issue "Flight ranking UX" $'Explain rank_reason strings; expose deep link prominently.' "mvp-3-flights-lite"

create_issue "BookingAdapter partner research" $'Evaluate affiliate APIs; keep NoOp adapter until contract signed.\n\nRefs: docs/booking/booking-adapter.md, services/api/skiplanner_api/booking/adapter.py' "future-booking-adapter"

echo "Done. Milestones and issues ensured in ${REPO}."
