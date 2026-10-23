# Mobile Stack Decision

## React Native vs Flutter

| Factor | React Native | Flutter |
|--------|-------------|---------|
| Market share (global) | ~3x more job postings | Growing but smaller |
| Code reuse with web | Types, API, utils via `shared/` | None (Dart vs TS) |
| Learning curve for team | Minimal (already React/TS) | Full new language |
| Portfolio value | High (wider market) | Niche but recognizable |
| Performance | Good (JSI bridge) | Excellent (Impeller) |

**Decision:** React Native (Expo SDK 57) — maximizes code reuse from the existing React/TypeScript web frontend and aligns with market demand.
