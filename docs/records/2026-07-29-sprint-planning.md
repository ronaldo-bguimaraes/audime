# Sprint Plan — Next 1-2 Sprints

> **Author**: scrum_master
> **Date**: 2026-07-29
> **Status**: Planning Complete — Ready for Refinement Step

---

## Executive Summary

The previous sprint (Cycle 10 — "All 11 Issues") resolved 9 of 11 issues, leaving **#3 (Google OAuth)** and **#5 (Fluxo Extração)** untouched. After thorough discovery, we found that **#5 is actually >90% implemented** through previous issues (#9, #11, #13, #14, #15, #19, #20, #23). The dashboard (#4) is also largely complete (backend done, frontend with Real-time charts).

The two recommended sprints are:

| Sprint | Focus | Issues | Effort |
|--------|-------|--------|--------|
| **Sprint A** | Google OAuth | #3 | **LARGE** |
| **Sprint B** | Dashboard Polish + Extraction Verification | #4 (remaining) | **SMALL** |

These sprints can be run sequentially or in parallel since they touch different code layers (auth vs. dashboard/extraction).

---

## Current State Assessment

### What's DONE (verified in Cycle 10)

| # | Issue | Status | Notes |
|---|-------|--------|-------|
| #6 | Parser MG | ✅ Done | 28/29 tests pass, MgParser implemented |
| #7 | Spam hint | ✅ Done | Playwright test passing |
| #8 | Refresh code screen | ✅ Done | Playwright test passing |
| #12 | Force-reset extração | ✅ Done | 7/7 tests passing |
| #16 | Dashboard empty state | ✅ Done | Playwright test passing |
| #17 | Fix MG fixture | ✅ Done | All 10+ MG tests pass |

### What's PARTIALLY DONE

| # | Issue | What's Done | What Remains |
|---|-------|-------------|--------------|
| #4 | Dashboard Financeiro | ✅ Backend (29/29 tests), ✅ Frontend with Recharts (BarChart + PieChart + cards), ✅ Empty state | ⏳ Playwright tests for loading/error states, ⏳ Mobile responsive verification |
| #5 | Fluxo Extração NFC-e | ✅ Page `/extrair` with URL form + QR scanner + history list + polling + reprocess; ✅ ExtracaoDetalhe page with timeline; ✅ QrCodeScanner component; ✅ QrCodeDisplay component; ✅ Full backend CRUD | ⏳ End-to-end Playwright tests, ⏳ Integration verification |

### What's NOT STARTED

| # | Issue | Effort | Dependencies |
|---|-------|--------|-------------|
| #3 | Google OAuth | **LARGE** | Setup Frontend (#2 — ✅ done) |

---

## Sprint A: Google OAuth (#3)

### Rationale

Google OAuth is the highest-impact missing feature. It:
1. Provides a frictionless login experience for end users
2. Is the single largest piece of remaining work
3. Is self-contained — touches only auth layer (backend + frontend)
4. Does NOT block #4 or #5 development (they work with mock data and existing passwordless auth)

### Effort Estimate: **LARGE** (5-8 days)

### Architecture

**Current auth system:**
- Backend: JWT (HS256) + email verification code (passwordless)
- Frontend: AuthProvider context, localStorage token storage, PrivateRoute guard

**Google OAuth addition:**
```
Frontend: "Entrar com Google" button → Google OAuth popup → ID token → POST /v1/auth/google
Backend:  POST /v1/auth/google → validate token with google-auth → create/find user → return JWT
```

### Acceptance Criteria

#### Backend (5 criteria)

- [ ] **CAT-OAUTH-001**: `POST /v1/auth/google` endpoint exists, accepts `{ credential: string }` (Google ID token)
      **Test**: `pytest tests/test_auth_flow.py::test_google_endpoint_exists -v`

- [ ] **CAT-OAUTH-002**: Google ID token is validated using `google.oauth2.id_token.verify_oauth2_token()` — checks audience (GOOGLE_CLIENT_ID), issuer (`accounts.google.com`), and cryptographic signature
      **Test**: `pytest tests/test_auth_flow.py::test_google_invalid_token_returns_401 -v`

- [ ] **CAT-OAUTH-003**: New Google user (first login) is auto-created in `core.usuario` with name and email from Google profile; returns JWT in same format as existing auth `{ status: "ok", access_token: "...", id_usuario: N }`
      **Test**: `pytest tests/test_auth_flow.py::test_google_creates_new_user -v`

- [ ] **CAT-OAUTH-004**: Existing Google user (subsequent login) returns JWT without creating duplicate
      **Test**: `pytest tests/test_auth_flow.py::test_google_existing_user -v`

- [ ] **CAT-OAUTH-005**: `GOOGLE_CLIENT_ID` is configurable via `.env` variable; existing passwordless auth (`POST /v1/auth/code`, `POST /v1/auth/verify`) continues to work with zero regression
      **Test**: `pytest tests/test_auth_flow.py -v` — all existing passwordless tests pass (3 tests)

#### Frontend (5 criteria)

- [ ] **CAT-OAUTH-006**: "Entrar com Google" button appears on `/login` page with Google-branded styling (G logo + "Entrar com Google" text), positioned below the email form
      **Test**: Playwright test: verifies button text and clickability

- [ ] **CAT-OAUTH-007**: Clicking "Entrar com Google" opens Google OAuth popup (using `window.google.accounts.id` — Google Identity Services library via script tag); on successful authentication, the ID token is sent to `POST /v1/auth/google`; the returned JWT is stored in `localStorage` as `audime_token`
      **Test**: Playwright test with mocked GIS library callback

- [ ] **CAT-OAUTH-008**: After successful Google login, user is redirected to `/dashboard`; user info (name, email) is fetched via `GET /v1/auth/me`
      **Test**: Playwright test: verify redirect + user info display in header

- [ ] **CAT-OAUTH-009**: Error handling: popup blocked by browser shows user-friendly message ("Popup bloqueado. Permita popups para este site."); network error shows retry option; invalid token shows "Falha na autenticação. Tente novamente."
      **Test**: Playwright test: mock popup blocked scenario, verify message

- [ ] **CAT-OAUTH-010**: Logout clears both Google session and JWT; token expiry redirects to `/login` without crash (same behavior as existing passwordless auth)
      **Test**: Playwright test: logout → verify redirect to `/login`; expired token → verify redirect to `/login`

### Backend Implementation Plan

1. **Add `google-auth` dependency** to `requirements.txt` / `pyproject.toml`
2. **Add `GOOGLE_CLIENT_ID` to Settings** in `app/core/config.py`
3. **Create `GoogleAuthRequest` schema** in `app/api/v1/schemas.py`
4. **Add `POST /v1/auth/google` endpoint** in `app/api/v1/endpoints/auth.py`:
   - Receive `{ credential: string }`
   - Call `google.oauth2.id_token.verify_oauth2_token(credential, requests.Request(), GOOGLE_CLIENT_ID)`
   - Extract `sub` (Google user ID), `email`, `name`, `picture`
   - Look up user by Google `sub` (store in new column `google_sub` on `Usuario`) or by email
   - If new: create `Usuario` with `google_sub`, name, email
   - If existing: update `google_sub` if not set (link accounts)
   - Create JWT using existing `create_access_token(str(user.id_usuario))`
   - Return `{ status: "ok", access_token, id_usuario }`
5. **Add `google_sub` column** to `Usuario` model and create Alembic migration
6. **Add tests** for all error/success scenarios

### Frontend Implementation Plan

1. **Add Google Identity Services script** to `web/index.html`:
   ```html
   <script src="https://accounts.google.com/gsi/client" async defer></script>
   ```
2. **Create `GoogleLoginButton` component** in `web/src/components/GoogleLoginButton.tsx`
3. **Integrate into Login page** — render below email form
4. **Update `AuthProvider`** to handle Google auth (store token on callback)
5. **Write Playwright tests** for all scenarios
6. **Handle Google One Tap** if user is already signed in (optional, nice-to-have)

### Files to Change

| File | Action |
|------|--------|
| `requirements.txt` / `pyproject.toml` | Add `google-auth>=2.0` |
| `app/core/config.py` | Add `GOOGLE_CLIENT_ID: str = ""` |
| `abstract/models/core.py` | Add `google_sub` column to `Usuario` |
| `alembic/versions/` | Add migration for `google_sub` |
| `app/api/v1/schemas.py` | Add `GoogleAuthRequest` schema |
| `app/api/v1/endpoints/auth.py` | Add `POST /v1/auth/google` endpoint |
| `app/api/v1/schemas.py` | Update auth response schemas if needed |
| `web/index.html` | Add Google GSI script |
| `web/src/components/GoogleLoginButton.tsx` | **NEW** — Google OAuth button component |
| `web/src/pages/Login.tsx` | Add GoogleLoginButton below email form |
| `web/src/hooks/useAuth.tsx` | Add `loginWithGoogle` method |
| `web/src/api/auth.ts` | Add `googleLogin(token)` function |
| `tests/test_auth_flow.py` | Add 5+ test cases for Google OAuth |
| `web/tests/` | Add Playwright tests for Google login flow |

---

## Sprint B: Dashboard Polish + Extraction Verification

### Rationale

After Sprint A (or in parallel), the remaining work is primarily **validation and polish**:
- Dashboard needs Playwright tests for loading/error states + responsive check
- Extraction flow needs end-to-end verification
- Board needs cleanup (#6, #17 status update to Done)

### Effort Estimate: **SMALL** (2-3 days)

### Acceptance Criteria

#### Dashboard (#4 remaining)

- [ ] **CAT-DASH-001**: Loading state shows `<LoadingSpinner />` while `GET /v1/dashboard/resumo` is pending
      **Test**: Playwright test with delayed mock response

- [ ] **CAT-DASH-002**: Error state (API failure) shows error message with "Tentar novamente" button that retries the fetch
      **Test**: Playwright test with mocked API error

- [ ] **CAT-DASH-003**: Dashboard is responsive at mobile breakpoint (< 700px): cards stack vertically, sidebar collapses, text doesn't overflow
      **Test**: Playwright test with viewport width 375px; verify no horizontal scroll, cards are full-width

- [ ] **CAT-DASH-004**: `npm run build` compiles without errors; `npx tsc --noEmit` passes
      **Test**: CI verification

#### Extraction Flow (#5 verification)

Since the extraction flow is already heavily implemented through prior issues, these criteria verify the end-to-end integration:

- [ ] **CAT-FLOW-001**: Navigation: clicking an extraction row on `/extrair` navigates to `/extracao/:id` detail page
      **Test**: Playwright test — click row, verify URL changes

- [ ] **CAT-FLOW-002**: Detail page (`/extracao/:id`) shows QR Code from URL, step timeline, "Abrir" and "Copiar" buttons
      **Test**: Playwright tests from issue #19 (QR Code display) — already passing

- [ ] **CAT-FLOW-003**: Polling stops when no extraction is PENDING/RUNNING
      **Test**: Integration test or code review — `setInterval` cleared when all statuses are terminal

- [ ] **CAT-FLOW-004**: `npm run build` compiles without errors; `npx tsc --noEmit` passes
      **Test**: CI verification

- [ ] **CAT-FLOW-005**: Mock mode (`VITE_USE_MOCK=true`) allows full extraction flow without backend
      **Test**: `npm run dev` with mock mode — verify form submission shows mock extraction in list

#### Board Cleanup

- [ ] **CAT-BOARD-001**: Move issues #6 (MG Parser) and #17 (MG Fixture) to **Done** on project board #5
      **Action**: `gh project item-edit` commands

- [ ] **CAT-BOARD-002**: Ensure all items in Sprint B are tracked on board with correct status
      **Action**: Add new issues if needed, move to In Progress

### Files to Change

| File | Action |
|------|--------|
| `web/src/pages/Dashboard.tsx` | Minor: verify loading/error patterns exist |
| `web/tests/dashboard-loading.spec.ts` | **NEW** — Playwright tests for loading/error |
| `web/tests/extraction-flow.spec.ts` | **NEW** — Playwright tests for extraction flow |
| `.agents/workspace/specification.md` | Update with Sprint B criteria |

---

## Dependency Graph

```
Sprint A (Google OAuth)          Sprint B (Dashboard + Extraction)
         │                                │
         │  ┌─────────────────────────────┘
         │  │  (can be parallel or sequential)
         ▼  ▼
    ┌─────────────┐
    │  Validation  │
    │  (QA + DevOps)│
    └─────────────┘
         │
         ▼
    ┌─────────────┐
    │   Review &   │
    │   Archive    │
    └─────────────┘
```

- **No hard dependency** between Sprint A and Sprint B
- Sprint B's dashboard tests work with mock data (#23 — already done)
- Sprint B's extraction flow tests work with mock data or existing backend
- Recommend running Sprint A first (higher impact), then Sprint B
- Alternatively: run both in parallel with separate branches

---

## Risk Assessment

| Risk | Sprint | Likelihood | Impact | Mitigation |
|------|--------|------------|--------|------------|
| Google OAuth library compatibility | A | Low | High | Use well-documented `google-auth`; test against dev credentials first |
| Google OAuth popup blocked by browser | A | Medium | Medium | Add user-friendly "allow popups" message; test in CI with `--no-sandbox` |
| Dashboard Playwright flaky tests | B | Medium | Low | Use mock API interceptors; add `retries: 2` in Playwright config |
| Extraction flow already works — unnecessary work | B | Medium | Low | Focus on **verification only**, not reimplementation; skip if all tests pass |
| Board permissions for automation | Both | Low | Medium | Use `gh` CLI with proper token scopes (`repo`, `project`) |

---

## Recommendations

1. **Start with Sprint A** (Google OAuth) — it's the highest-impact missing feature and well-defined
2. **Run Sprint B in parallel** if capacity allows — dashboard + extraction verification are lighter tasks
3. **Update project board** as part of Sprint B to reflect true status of #6, #17
4. **Add CI for Playwright** — the previous sprint had 8 Playwright failures (7 due to missing backend). Add `docker-compose.test.yml` for test environment with backend + frontend
5. **Tag releases** after each sprint to track progress on GitHub
