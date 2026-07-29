# Audime Mobile

> React Native (Expo) version of the Audime app for Android and iOS.

## Decision

React Native was chosen over Flutter for the mobile implementation. See `docs/architecture/mobile-stack.md` for rationale.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React Native (Expo SDK 57) |
| Language | TypeScript |
| Navigation | expo-router |
| State | React Context + hooks |
| API | Shared client from `shared/` package |
| Auth | Email-based code (same as web) |

## Project Structure

```
mobile/
├── App.tsx           ← Root component
├── app/              ← expo-router pages
├── src/
│   ├── components/   ← Reusable UI components
│   └── hooks/        ← React hooks (useAuth, useFetch, etc.)
├── assets/           ← Icons, splash screen
├── app.json          ← Expo config
└── package.json
```

## Development

```bash
cd mobile
npx expo start
```

Scan the QR code with Expo Go (Android/iOS) to run.

## Shared Package

Both `mobile/` and `web/` import types, API client, and utils from the `shared/` package at the root:

```
shared/
├── src/
│   ├── types/        ← Interfaces (AuthState, Nota, DashboardResumo, etc.)
│   ├── api/          ← Client factory + endpoint modules + mock
│   └── utils/        ← formatBRL, maskChave, formatDate
└── package.json
```

## Build

```bash
# Android APK
npx expo run:android

# iOS IPA
npx expo run:ios
```
