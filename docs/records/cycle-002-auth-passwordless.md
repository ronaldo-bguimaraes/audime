# Cycle 002 — Passwordless Authentication (email + code)

**Date**: 2026-06-30

## Summary
Implementation of passwordless authentication with a 6-digit code sent via email (LogEmailSender in dev). JWT with HS256, automatic user creation, basic rate limiting.

## What was done
1. `AuthCode` model in `abstract/models/auth.py` — code hash, expiry, attempts
2. Abstract `EmailSender` + `LogEmailSender` for dev
3. `auth_service.py` — code generation, hashing, JWT, verification, rate limiting
4. Endpoints: `POST /v1/auth/code`, `POST /v1/auth/verify`, `GET /v1/auth/me`
5. `get_current_user_id()` now reads from JWT via `HTTPBearer`
6. `Settings` with `JWT_SECRET` and `JWT_ALGORITHM`
7. `conftest.py` with `schema_translate_map` for SQLite testing
8. 3 integration tests (full flow, invalid code, missing token)

## Criteria
✅ 12/12 criteria met

## Project state
- Backend compiles ✅
- 4 passing tests (1 placeholder + 3 auth) ✅
- Authentication working with JWT ✅
- Endpoints protected by `Depends(get_current_user_id)` ✅
- Next cycle: NFC-e extraction flow (#5) or web frontend (#1/#2)
