# skiMate — Mobile App

React Native / Expo app for iOS and Android.

## Prerequisites

- Node.js 20+
- [Expo CLI](https://docs.expo.dev/get-started/installation/)
- iOS Simulator (Xcode) or Android emulator — or a physical device with Expo Go

## Setup

### 1. Install dependencies

```bash
npm install
```

### 2. Configure the API base URL

The app reads the API base URL from `app.json` → `expo.extra.apiBaseUrl`.

| Scenario | Value |
|----------|-------|
| Local dev (simulator) | `http://localhost:8040` (default) |
| Physical device on LAN | `http://192.168.1.10:8040` (use your machine's IP) |
| Staging | `https://api-staging.skimate.app` |

Edit `app.json`:
```json
"extra": { "apiBaseUrl": "http://YOUR_LAN_IP:8040" }
```

### 3. Map provider keys

The map view feature (issue #9) requires either Mapbox or Google Maps.

- **Mapbox:** set `MAPBOX_PUBLIC_TOKEN` in your `.env`, then add it to `app.json` → `expo.extra.mapboxToken`
- **Google Maps:** set `GOOGLE_MAPS_API_KEY` in your `.env` and follow the [Expo MapView setup guide](https://docs.expo.dev/versions/latest/sdk/map-view/)

Never commit real keys. Add them to `.env` locally (gitignored), and as GitHub Actions secrets for CI/CD.

## Run

```bash
npx expo start           # Expo dev server (scan QR with Expo Go)
npx expo start --ios     # iOS Simulator
npx expo start --android # Android emulator
```

## Project structure

```
apps/mobile/
  app/              ← Expo Router routes (_layout.tsx, index.tsx, resort/[id].tsx)
  src/
    screens/        ← Screen components
    components/     ← Shared UI components
    hooks/          ← Custom React hooks
    services/       ← API client
    constants/      ← Design tokens (colors, spacing, typography)
  assets/           ← Icons and splash images
```

## GitHub Actions secrets

| Secret | Purpose |
|--------|---------|
| `AMADEUS_CLIENT_ID` | Amadeus flight search |
| `AMADEUS_CLIENT_SECRET` | Amadeus flight search |
| `EXPO_PUBLIC_API_BASE_URL` | API base URL for staging builds |
| `MAPBOX_PUBLIC_TOKEN` | Map rendering |
| `GOOGLE_MAPS_API_KEY` | Map rendering (alternative) |

Full list and setup instructions: `docs/infra/ci-secrets.md`
