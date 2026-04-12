# ADR 001: Mobile stack and monorepo layout

## Status

Accepted (MVP foundation).

## Context

Product name: **skiMate** (GitHub repository may remain `SkiPlannerAI`). We need iOS and Android from one codebase, a clear repo layout for a three-person team, and a documented way to manage secrets.

## Decision

- **Mobile:** **Expo (React Native)** with TypeScript.
  - Strong ecosystem for maps (Mapbox / Google Maps via community modules).
  - Fast iteration and OTA-friendly workflow for MVP.
  - Alternative considered: Flutter (excellent map performance; team would need Dart ramp-up).

- **Backend (MVP):** **FastAPI** under `services/api/` (aligns with Python tooling already in the repo).

- **Layout:**

  - `apps/mobile/` — Expo app.
  - `services/api/` — REST API, ingest helpers, flight ranking.
  - `docs/` — specs, ADRs, QA checklists.
  - `data/seed/` — curated resort seeds and GeoJSON map snippets.

- **Secrets:** Never commit `.env`. Copy `.env.example` to `.env` locally and in CI use injected secrets. Document required keys in `README.md` and `.env.example`.

## Consequences

- Developers run API and mobile separately during MVP (API on localhost, Expo with dev client / tunnel as needed).
- Map provider API keys for production are mobile-app concerns; document in `apps/mobile/README.md`.
